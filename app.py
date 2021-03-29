#!/usr/bin/env python3

import aws_cdk.aws_dynamodb as dynamodb
from aws_cdk.core import App, Environment, Stack, Construct
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_s3 import Bucket, HttpMethods
from aws_cdk.aws_lambda import Function, Code, Runtime
from aws_cdk.aws_apigateway import RestApi, LambdaIntegration, Cors

STORAGE_ID = "Votes"

app = App()
env = Environment(region="eu-central-1", account="685178144596")
tags = {
    "Project": "slurm-student-voting-app",
}


class VotingStorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        Table(
            self,
            id=STORAGE_ID,
            table_name=STORAGE_ID,
            partition_key=Attribute(name="voter", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )


class VotingVoteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="voting-frontend",
            bucket_name="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )


class VotingResultStack(Stack):
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
            function_name="result-backend-function",
            code=Code.asset("./result-backend"),
            handler="results.lambda_handler",
            runtime=Runtime.PYTHON_3_8,
        )

        dbtable = dynamodb.Table.from_table_name(
            self, STORAGE_ID, table_name=STORAGE_ID
        )
        dbtable.grant_read_data(handler)

        rest_gw = RestApi(
            self,
            id="result-gateway",
            rest_api_name="result-gateway-api",
            default_cors_preflight_options={
                "allow_origins": Cors.ALL_ORIGINS,
                "allow_methods": Cors.ALL_METHODS,
            },
        )
        gw_resource = rest_gw.root.add_resource("my-vote")
        gw_resource_lambda_integration = LambdaIntegration(
            handler,
            proxy=True,
            integration_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": "'*'",
                    },
                }
            ],
        )
        gw_resource.add_method(
            "GET",
            gw_resource_lambda_integration,
            method_responses=[
                {
                    "statusCode": "200",
                    "responseParameters": {
                        "method.response.header.Access-Control-Allow-Origin": True,
                    },
                }
            ],
        )


VotingStorageStack(app, "voting-app-storage-stack", env=env, tags=tags)
VotingResultStack(app, "voting-app-result-stack", env=env, tags=tags)
# VotingVoteStack(app, "voting-app-voting-stack", env=env, tags=tags)

app.synth()
