#!/usr/bin/env python3

import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk.core import App, Environment, Stack, Construct
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_sns import Topic
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_lambda_destinations import SnsDestination
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_apigatewayv2 import HttpApi, HttpMethod, CorsHttpMethod
from aws_cdk.aws_apigatewayv2_integrations import LambdaProxyIntegration

STORAGE_ID = "Votes"

app = App()
env = Environment(region="eu-central-1", account="685178144596")
tags = {
    "Project": "slurm-student-voting-app",
}


class StorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Table(
            self,
            id=STORAGE_ID,
            table_name=STORAGE_ID,
            partition_key=Attribute(name="voter", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )


class VoteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = Topic(
            self,
            "my-vote",
            topic_name="my-vote",
            display_name="voting-keeper",
        )

        handler = Function(
            self,
            id="voting-backend",
            function_name="voting-backend-fun",
            code=Code.asset("./voting-backend"),
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

        handler = Function(
            self,
            id="result-backend",
            function_name="result-backend-fun",
            code=Code.asset("./result-backend"),
            handler="results.lambda_handler",
            runtime=Runtime.PYTHON_3_8,
        )

        dbtable = dynamodb.Table.from_table_name(
            self, STORAGE_ID, table_name=STORAGE_ID
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


StorageStack(app, "voting-app-storage-stack", env=env, tags=tags)
ResultStack(app, "voting-app-result-stack", env=env, tags=tags)
VoteStack(app, "voting-app-voting-stack", env=env, tags=tags)

app.synth()
