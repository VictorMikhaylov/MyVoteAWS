#!/usr/bin/env python3
import aws_cdk.aws_apigatewayv2 as apigw
import aws_cdk.aws_apigatewayv2_integrations as apigw_int
import aws_cdk.aws_cloudfront as cloudfront
import aws_cdk.aws_cloudfront_origins as origins
import aws_cdk.aws_dynamodb as dynamodb
import aws_cdk.aws_lambda as lmbda
import aws_cdk.aws_lambda_destinations as lambda_dest
import aws_cdk.aws_lambda_event_sources as lambda_es
import aws_cdk.aws_s3 as s3
import aws_cdk.aws_sns as sns
import aws_cdk.aws_sns_subscriptions as sns_subs
import aws_cdk.aws_sqs as sqs
import aws_cdk.core as core

ENV_REGION = "eu-central-1"
ENV_ACCAUNT = "685178144596"
STORAGE_ID = "Votes"
SQS_QUEUE_ID = "votes-queue"

app = core.App()
env = core.Environment(region=ENV_REGION, account=ENV_ACCAUNT)
tags = {
    "Project": "slurm-student-voting-app",
}


class StorageStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        dbtable = dynamodb.Table(
            self,
            id=STORAGE_ID,
            table_name=STORAGE_ID,
            partition_key=dynamodb.Attribute(name="voter", type=dynamodb.AttributeType.STRING),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,
        )

        queue = sqs.Queue(
            self,
            SQS_QUEUE_ID,
            queue_name=SQS_QUEUE_ID,
        )

        handler = lmbda.Function(
            self,
            id="vote-processor",
            function_name="vote-processor-fun",
            code=lmbda.Code.from_asset("./vote-processor", exclude=["README.md"]),
            handler="processor.lambda_handler",
            runtime=lmbda.Runtime.PYTHON_3_8,
        )
        handler.add_event_source(lambda_es.SqsEventSource(queue))
        dbtable.grant_write_data(handler)


class VotingStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        topic = sns.Topic(
            self,
            "my-vote",
            topic_name="my-vote",
            display_name="voting-keeper",
        )
        processor_queue = sqs.Queue.from_queue_attributes(
            self,
            SQS_QUEUE_ID,
            queue_arn=f"arn:aws:sqs:{ENV_REGION}:{ENV_ACCAUNT}:{SQS_QUEUE_ID}",
        )
        topic.add_subscription(sns_subs.SqsSubscription(processor_queue))
        topic.add_subscription(
            sns_subs.EmailSubscription(email_address="victor.v.mikhaylov@gmail.com", json=True)
        )

        handler = lmbda.Function(
            self,
            id="voting-backend",
            function_name="voting-backend-fun",
            code=lmbda.Code.from_asset("./voting-backend", exclude=["README.md"]),
            handler="voting.lambda_handler",
            runtime=lmbda.Runtime.PYTHON_3_8,
            on_success=lambda_dest.SnsDestination(topic),
        )

        bucket = s3.Bucket(
            self,
            id="voting-frontend",
            bucket_name="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        api_gateway = apigw.HttpApi(
            self,
            "voting-gateway",
            cors_preflight={
                "allow_headers": ["Accept", "Content-Type"],
                "allow_methods": [apigw.CorsHttpMethod.POST],
                "allow_origins": [f"{bucket.bucket_website_url}"],
            },
        )
        api_gateway.add_routes(
            path="/my-vote",
            methods=[apigw.HttpMethod.POST],
            integration=apigw_int.LambdaProxyIntegration(handler=handler),
        )


class ResultStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = s3.Bucket(
            self,
            id="result-frontend",
            bucket_name="result-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        dbtable = dynamodb.Table.from_table_name(self, STORAGE_ID, table_name=STORAGE_ID)

        handler = lmbda.Function(
            self,
            id="result-backend",
            function_name="result-backend-fun",
            code=lmbda.Code.from_asset("./result-backend", exclude=["README.md"]),
            handler="results.lambda_handler",
            runtime=lmbda.Runtime.PYTHON_3_8,
        )
        dbtable.grant_read_data(handler)

        api_gateway = apigw.HttpApi(
            self,
            id="result-gateway",
            cors_preflight={
                "allow_headers": ["Accept", "Content-Type"],
                "allow_methods": [apigw.CorsHttpMethod.GET],
                "allow_origins": [f"{bucket.bucket_website_url}"],
            },
        )
        api_gateway.add_routes(
            path="/my-vote",
            methods=[apigw.HttpMethod.GET],
            integration=apigw_int.LambdaProxyIntegration(handler=handler),
        )


class CloudFrontStack(core.Stack):
    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        voting_bucket = s3.Bucket(
            self,
            id="voting-frontend-cf",
            bucket_name="voting-frontend-cf-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        result_bucket = s3.Bucket(
            self,
            id="result-frontend-cf",
            bucket_name="result-frontend-cf-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

        voting_origin = origins.S3Origin(voting_bucket)
        result_origin = origins.S3Origin(result_bucket)

        cfd = cloudfront.Distribution(
            self,
            id="slurm-voting-distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=voting_origin,
                allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
                cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                compress=True,
            ),
            default_root_object="index.html",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100,
        )
        cfd.add_behavior(
            "/results/*",
            origin=result_origin,
            allowed_methods=cloudfront.AllowedMethods.ALLOW_GET_HEAD,
            cached_methods=cloudfront.CachedMethods.CACHE_GET_HEAD,
            viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
            compress=True,
        )


CloudFrontStack(app, "voting-app-cloudfront-stack", env=env, tags=tags)
StorageStack(app, "voting-app-storage-stack", env=env, tags=tags)
VotingStack(app, "voting-app-voting-stack", env=env, tags=tags)
ResultStack(app, "voting-app-result-stack", env=env, tags=tags)

app.synth()
