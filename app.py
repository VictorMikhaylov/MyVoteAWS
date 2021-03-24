#!/usr/bin/env python3

from aws_cdk.core import App, Environment, Stack, Construct
from aws_cdk.aws_dynamodb import Table, Attribute, AttributeType, BillingMode
from aws_cdk.aws_s3 import Bucket
from aws_cdk.aws_lambda import Function, Code, Runtime

app = App()
env = Environment(region="eu-central-1", account="685178144596")
tags = {
    "Project": "slurm-student-voting-app",
}


class VotingStorageStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        votes_table = Table(
            self,
            id="Votes",
            table_name="Votes",
            partition_key=Attribute(name="voter", type=AttributeType.STRING),
            billing_mode=BillingMode.PAY_PER_REQUEST,
        )


class VotingVoteStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        bucket = Bucket(
            self,
            id="voting-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )


class VotingResultStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        handler = Function(
            self,
            id="UrlShortenerFunction",
            code=Code.asset("./result-backend"),
            handler="results.handler",
            runtime=Runtime.PYTHON_3_7,
        )
        bucket = Bucket(
            self,
            id="result-frontend-bkt",
            public_read_access=True,
            website_index_document="index.html",
        )


VotingStorageStack(app, "voting-app-storage-stack", env=env, tags=tags)
VotingResultStack(app, "voting-app-result-stack", env=env, tags=tags)
VotingVoteStack(app, "voting-app-voting-stack", env=env, tags=tags)

app.synth()
