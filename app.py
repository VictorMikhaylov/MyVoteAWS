#!/usr/bin/env python3

from aws_cdk.core import App, Environment, Stack, Construct
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_cloudfront import (
    BehaviorOptions,
    Distribution,
    AllowedMethods,
    ViewerProtocolPolicy,
)
from aws_cdk.aws_cloudfront_origins import S3Origin
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_sns_subscriptions import EmailSubscription, SqsSubscription
from aws_cdk.aws_sqs import Queue
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_lambda_event_sources import SqsEventSource
from aws_cdk.aws_lambda_destinations import SnsDestination
from aws_cdk.aws_apigatewayv2 import HttpApi, HttpMethod, CorsHttpMethod
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode

ENV_REGION = "eu-central-1"
ENV_ACCAUNT = "685178144596"
STORAGE_ID = "Votes"
SQS_QUEUE_ID = "votes-queue"

app = App()
env = Environment(region=ENV_REGION, account=ENV_ACCAUNT)
tags = {
    "Project": "slurm-student-voting-app",
}


class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dbtable = Table(
            self,
            id=STORAGE_ID,
            table_name=STORAGE_ID,
            partition_key=Attribute(name="voter", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

        queue = Queue(
            self,
            SQS_QUEUE_ID,
            queue_name=SQS_QUEUE_ID,
        )

        handler = Function(
            self,
            id="vote-processor",
            function_name="vote-processor-fun",
            code=Code.from_asset("./vote-processor", exclude=["README.md"]),
            handler="processor.lambda_handler",
            runtime=Runtime.PYTHON_3_8,
        )
        handler.add_event_source(SqsEventSource(queue))
        dbtable.grant_write_data(handler)


class VotingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = Topic(
            self,
            "my-vote",
            topic_name="my-vote",
            display_name="voting-keeper",
        )
        processor_queue = Queue.from_queue_attributes(
            self,
            SQS_QUEUE_ID,
            queue_arn=f"arn:aws:sqs:{ENV_REGION}:{ENV_ACCAUNT}:{SQS_QUEUE_ID}",
        )
        topic.add_subscription(SqsSubscription(processor_queue))
        topic.add_subscription(
            EmailSubscription(email_address="victor.v.mikhaylov@gmail.com", json=True)
        )

        handler = Function(
            self,
            id="voting-backend",
            function_name="voting-backend-fun",
            code=Code.from_asset("./voting-backend", exclude=["README.md"]),
            handler="voting.lambda_handler",
            runtime=Runtime.PYTHON_3_8,
            on_success=SnsDestination(topic),
        )

        bucket = Bucket(
            self,
            id="voting-frontend",
            bucket_name="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        api_gateway = HttpApi(
            self,
            "voting-gateway",
            cors_preflight={
                "allow_headers": ["Accept", "Content-Type"],
                "allow_methods": [CorsHttpMethod.POST],
                "allow_origins": [f"{bucket.bucket_website_url}"],
            },
        )
        api_gateway.add_routes(
            path="/my-vote",
            methods=[HttpMethod.POST],
            integration=LambdaProxyIntegration(handler=handler),
        )


class ResultStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="result-frontend",
            bucket_name="result-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        dbtable = Table.from_table_name(self, STORAGE_ID, table_name=STORAGE_ID)

        handler = Function(
            self,
            id="result-backend",
            function_name="result-backend-fun",
            code=Code.from_asset("./result-backend", exclude=["README.md"]),
            handler="results.lambda_handler",
            runtime=Runtime.PYTHON_3_8,
        )
        dbtable.grant_read_data(handler)

        api_gateway = HttpApi(
            self,
            "result-gateway",
            cors_preflight={
                "allow_headers": ["Accept", "Content-Type"],
                "allow_methods": [CorsHttpMethod.GET],
                "allow_origins": [f"{bucket.bucket_website_url}"],
            },
        )
        api_gateway.add_routes(
            path="/my-vote",
            methods=[HttpMethod.GET],
            integration=LambdaProxyIntegration(handler=handler),
        )


class CloudFrontStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        voting_bucket = Bucket(
            self,
            id="voting-frontend-cf",
            bucket_name="voting-frontend-cf-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        result_bucket = Bucket(
            self,
            id="result-frontend-cf",
            bucket_name="result-frontend-cf-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        cfd = Distribution(
            self,
            "voting-distribution",
            default_behavior=BehaviorOptions(
                origin=S3Origin(voting_bucket),
                allowed_methods=AllowedMethods.ALLOW_GET_HEAD,
                viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                compress=True,
            ),
        )
        cfd.add_behavior(
            "results/*",
            origin=S3Origin(result_bucket),
            allowed_methods=AllowedMethods.ALLOW_GET_HEAD,
            viewer_protocol_policy=ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            compress=True,
        )


CloudFrontStack(app, "voting-app-cloudfront-stack", env=env, tags=tags)
StorageStack(app, "voting-app-storage-stack", env=env, tags=tags)
VotingStack(app, "voting-app-voting-stack", env=env, tags=tags)
ResultStack(app, "voting-app-result-stack", env=env, tags=tags)

app.synth()
