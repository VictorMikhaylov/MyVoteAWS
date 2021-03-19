#!/usr/bin/env python3

from aws_cdk import core

from voting_deploy import VotingFrontendStack


app = core.App()

VotingFrontendStack(app, "my-voting-app", env=core.Environment(region="eu-central-1", account="685178144596"))

app.synth()
