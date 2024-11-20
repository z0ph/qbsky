#!/usr/bin/env python

import json
import logging
import requests
from datetime import datetime
from config import get_secret

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
    # Process text to ensure URLs are on their own line
    processed_text = format_text_with_urls(text)
    
    response = requests.post(
        "https://bsky.social/xrpc/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "repo": did,
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": processed_text,
                "createdAt": datetime.utcnow().isoformat() + "Z",
            },
        },
    )
    return response


def format_text_with_urls(text):
    """Format text to ensure URLs are on their own line"""
    import re
    
    # URL regex pattern
    url_pattern = r'https?://\S+'
    
    # Find all URLs in the text
    urls = re.finditer(url_pattern, text)
    
    # Process each URL
    last_end = 0
    result = []
    for match in urls:
        start, end = match.span()
        
        # Add text before URL
        before_url = text[last_end:start].rstrip()
        if before_url:
            result.append(before_url)
        
        # Add URL on its own line
        result.append(match.group())
        last_end = end
    
    # Add remaining text
    if last_end < len(text):
        remaining = text[last_end:].lstrip()
        if remaining:
            result.append(remaining)
    
    # Join with newlines
    return '\n'.join(result)


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
        logger.info(f"Processing message {processed_messages}/{total_messages} (ID: {message_id})")
        logger.debug(f"Raw message content: {message}")

        # Truncate message if too long (Bluesky limit is 300 characters)
        original_length = len(message)
        post = (message[:275] + "..") if original_length > 279 else message
        
        if original_length > 279:
            logger.warning(f"Message truncated from {original_length} to 277 characters")

        # Create post with both token and did
        logger.info(f"Posting to Bluesky (message {processed_messages}/{total_messages})")
        response = create_post(post, token, did)

        if response.status_code != 200:
            logger.error(f"Failed to post message {message_id}: {response.text}")
            raise Exception(f"Failed to post: {response.status_code}")

        logger.info(f"Successfully posted message {message_id} to Bluesky")

    logger.info(f"Successfully processed all {total_messages} messages")
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Successfully processed all messages",
            "processed_count": total_messages
        }),
    }
