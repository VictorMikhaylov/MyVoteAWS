#!/usr/bin/env python3

import dynamodb
from aws_cdk.core import App, Environment, Tag

vf = __import__("voting-frontend")
rf = __import__("result-frontend")
dd = __import__("dynamodb")


app = App()
env = Environment(region="eu-central-1", account="685178144596")
tags = {
    "Project": "slurm-student-voting-app",
}

vf_stack = vf.VotingFrontendStack(app, "voting-app-voting-bucket", env=env, tags=tags)
rf_stack = rf.ResultFrontendStack(app, "voting-app-result-bucket", env=env, tags=tags)
dynamo_storage = dd.VotingStorageStack(app, "voting-storage", env=env, tags=tags)

app.synth()
