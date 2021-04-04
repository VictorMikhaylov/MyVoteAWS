import boto3
import json
import logging
import sys

logging.getLogger().setLevel(logging.INFO)


def lambda_handler(event, context):
    vote = json.loads(event["body"])["vote"]
    batch = {
        "voter": "default_voter",
        "vote": vote,
    }

    logging.info("Vote: %s", batch)

    try:
        publish_vote(batch)
    except:
        e = sys.exc_info()[0]
        logging.error(e)
        return {"statusCode": 500, "body": '{"status": "error"}'}

    return {"statusCode": 200, "body": '{"status": "success"}'}


def publish_vote(batch):
    sns = boto3.client("sns", region_name="eu-central-1")
    sns.publish(
        TopicArn="arn:aws:sns:eu-central-1:685178144596:my-vote",
        Message=json.dumps(batch),
    )
    logging.info("message published")
