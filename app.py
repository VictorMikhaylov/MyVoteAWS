#!/usr/bin/env python3

import dynamodb
from aws_cdk.core import App, Environment, Stack, Construct
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_s3 import Bucket

app = App()
env = Environment(region="eu-central-1", account="685178144596")
tags = {
    "Project": "slurm-student-voting-app",
}

class VotingStorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        votes_table = Table(self, 
            id = "Votes",
            partition_key=Attribute(
                name="voter",
                type=AttributeType.STRING
            ),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )

class VotingFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

class ResultFrontendStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="result-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )

vf_stack = VotingFrontendStack(app, "voting-app-voting-bucket", env=env, tags=tags)
rf_stack = ResultFrontendStack(app, "voting-app-result-bucket", env=env, tags=tags)
dynamo_storage = VotingStorageStack(app, "voting-storage", env=env, tags=tags)

app.synth()
