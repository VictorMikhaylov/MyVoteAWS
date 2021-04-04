#!/usr/bin/env python

import boto3
import json
import logging

logging.getLogger().setLevel(logging.INFO)

# Get the service resource
table = boto3.resource("dynamodb", region_name="eu-central-1").Table("Votes")


def lambda_handler(event, context):
    for message in event["Records"]:
        logging.info("Body: %s", message["body"])
        body = json.loads(message["body"])
        logging.info("Payload: %s", body["Message"])
        payload = json.loads(body["Message"])
        process_message(payload)


def process_message(payload):
    voter = payload["voter"]
    vote = payload["vote"]
    logging.info("Voter: %s, Vote: %s", voter, vote)
    store_vote(voter, vote)
    update_count(vote)


def store_vote(voter, vote):
    try:
        response = table.put_item(Item={"voter": voter, "vote": vote})
    except:
        logging.error("Failed to store message")
        raise


def update_count(vote):
    table.update_item(
        Key={"voter": "count"},
        UpdateExpression="set #vote = #vote + :incr",
        ExpressionAttributeNames={"#vote": vote},
        ExpressionAttributeValues={":incr": 1},
    )
