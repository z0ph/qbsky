#!/usr/bin/env python

import json
import logging
import requests
from datetime import datetime
from config import get_secret
from typing import List, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()


def get_auth_token(handle, password):
    """Get authentication token from Bluesky"""
    auth_response = requests.post(
        "https://bsky.social/xrpc/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
    )
    response_json = auth_response.json()
    # Return both the token and did
    return response_json.get("accessJwt"), response_json.get("did")


def create_post(text, token, did):
    """Create a post on Bluesky"""
    # Parse text for URLs and create facets
    facets = parse_facets(text)

    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": text,  # Use original text, not processed
                "facets": facets,  # Add facets for links
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
        },
    )
    return response


def parse_urls(text: str) -> List[Dict]:
    """Parse URLs from text and return their byte spans"""
    spans = []
    # URL regex pattern
    url_regex = rb"[$|\W](https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*[-a-zA-Z0-9@%_\+~#//=])?)"
    text_bytes = text.encode("UTF-8")
    for m in re.finditer(url_regex, text_bytes):
        spans.append({
            "start": m.start(1),
            "end": m.end(1),
            "url": m.group(1).decode("UTF-8"),
        })
    return spans


def parse_facets(text: str) -> List[Dict]:
    """Parse text and create facets for URLs"""
    facets = []
    for u in parse_urls(text):
        facets.append({
            "index": {
                "byteStart": u["start"],
                "byteEnd": u["end"],
            },
            "features": [{
                "$type": "app.bsky.richtext.facet#link",
                "uri": u["url"],
            }],
        })
    return facets


def lambda_handler(event, context):
    """
    AWS Lambda handler that processes messages from SQS and posts them to Bluesky.

    Args:
        event: AWS Lambda event containing SQS messages
        context: AWS Lambda context
    """
    # Get credentials from AWS Secrets Manager
    logger.info("Retrieving credentials from Secrets Manager")
    secret = get_secret()

    # Get auth token and did from Bluesky
    logger.info(f"Authenticating with Bluesky handle: {secret['bluesky_handle']}")
    token, did = get_auth_token(secret["bluesky_handle"], secret["bluesky_password"])
    logger.info("Successfully authenticated with Bluesky")

    # Track message processing statistics
    total_messages = len(event["Records"])
    processed_messages = 0
    logger.info(f"Starting to process {total_messages} messages from SQS")

    # Process each message from SQS
    for record in event["Records"]:
        processed_messages += 1
        message = record["body"]
        message_id = record.get("messageId", "unknown")
        logger.info(
            f"Processing message {processed_messages}/{total_messages} (ID: {message_id})"
        )
        logger.debug(f"Raw message content: {message}")

        # Truncate message if too long (Bluesky limit is 300 characters)
        original_length = len(message)
        post = (message[:297] + "...") if original_length > 300 else message

        if original_length > 300:
            logger.warning(
                f"Message truncated from {original_length} to 300 characters"
            )

        # Create post with both token and did
        logger.info(
            f"Posting to Bluesky (message {processed_messages}/{total_messages})"
        )
        response = create_post(post, token, did)

        if response.status_code != 200:
            logger.error(f"Failed to post message {message_id}: {response.text}")
            raise Exception(f"Failed to post: {response.status_code}")

        logger.info(f"Successfully posted message {message_id} to Bluesky")

    logger.info(f"Successfully processed all {total_messages} messages")
    return {
        "statusCode": 200,
        "body": json.dumps(
            {
                "message": "Successfully processed all messages",
                "processed_count": total_messages,
            }
        ),
    }
