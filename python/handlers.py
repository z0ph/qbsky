#!/usr/bin/env python

import logging
from config import get_secret
import json
from atproto import Client

root = logging.getLogger()
if root.handlers:
    for handler in root.handlers:
        root.removeHandler(handler)
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

secret = get_secret()


def lambda_handler(event, context):
    client = Client()
    client.login(secret["bluesky_handle"], secret["bluesky_password"])

    for record in event["Records"]:
        logging.info("record: " + record["body"])
        raw_record = record["body"]
        logging.info("raw_length: " + str(len(raw_record)))
        post = (raw_record[:275] + "..") if len(raw_record) > 279 else raw_record
        logging.info("post_length: " + str(len(post)))
        logging.info("Publishing the queued post: " + post)

        client.send_post(post)

    body = {"message": "ACK", "event": event}

    response = {"statusCode": 200, "body": json.dumps(body)}

    return response
