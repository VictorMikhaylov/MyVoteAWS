#!/usr/bin/env python

import boto3
import logging

logging.getLogger().setLevel(logging.DEBUG)

# Get the service resource
table = boto3.resource("dynamodb", region_name="eu-central-1").Table("Votes")


def lambda_handler(event, context):
    for message in event["Records"]:
        logging.info(message["messageAttributes"])
        process_message(message["messageAttributes"])


def process_message(payload):
    voter = payload["voter"]["stringValue"]
    vote = payload["vote"]["stringValue"]
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
