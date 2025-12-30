"""FastAPI webhook server for PR code review automation."""

import hmac
import hashlib
import os
import re
import logging
from typing import Any

from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from dotenv import load_dotenv

from src.pr_processor import process_pr_review

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="PR Code Review Automation",
    description="Automated code review system for Bitbucket PRs using Claude Code CLI",
    version="1.0.0"
)

logger = logging.getLogger(__name__)

# Configuration
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "")

# Branch patterns for filtering
SOURCE_PATTERNS = [r"^feature/.*$", r"^fix/.*$"]
DEST_PATTERN = r"^development$"


def verify_signature(payload: bytes, signature: str) -> bool:
    """
    Verify Bitbucket webhook signature using HMAC-SHA256.

    Args:
        payload: Raw request body
        signature: X-Hub-Signature header value

    Returns:
        True if signature is valid, False otherwise
    """
    if not WEBHOOK_SECRET:
        logger.warning("Webhook secret not configured!")
        return True  # Pass in development mode

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    # Remove 'sha256=' prefix if present
    sig = signature[7:] if signature.startswith("sha256=") else signature

    return hmac.compare_digest(expected, sig)


def should_process_pr(source_branch: str, dest_branch: str) -> bool:
    """
    Check if PR matches the branch patterns for processing.

    Args:
        source_branch: Source branch name
        dest_branch: Destination branch name

    Returns:
        True if PR should be processed, False otherwise
    """
    source_match = any(re.match(p, source_branch) for p in SOURCE_PATTERNS)
    dest_match = re.match(DEST_PATTERN, dest_branch) is not None

    return source_match and dest_match


def extract_pr_info(payload: dict) -> dict:
    """
    Extract PR information from webhook payload.

    Args:
        payload: Webhook payload dictionary

    Returns:
        Dictionary with PR information
    """
    pr_data = payload.get("pullrequest", {})
    repo_data = payload.get("repository", {})

    return {
        "pr_id": pr_data.get("id"),
        "workspace": repo_data.get("workspace", {}).get("slug"),
        "repo_slug": repo_data.get("name"),
        "source_branch": pr_data.get("source", {}).get("branch", {}).get("name", ""),
        "dest_branch": pr_data.get("destination", {}).get("branch", {}).get("name", ""),
        "title": pr_data.get("title", ""),
        "author": payload.get("actor", {}).get("display_name", "Unknown")
    }


@app.post("/webhook")
async def webhook_handler(
    request: Request,
    background_tasks: BackgroundTasks
) -> dict[str, Any]:
    """
    Handle Bitbucket webhook events.

    Args:
        request: FastAPI request object
        background_tasks: Background task manager

    Returns:
        Response dictionary with status
    """
    # Get raw body for signature verification
    raw_body = await request.body()

    # Verify signature
    signature = request.headers.get("X-Hub-Signature", "")
    if not verify_signature(raw_body, signature):
        logger.warning("Invalid webhook signature!")
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Check event type - process both created and updated events
    event_type = request.headers.get("X-Event-Key", "")
    allowed_events = ["pullrequest:created", "pullrequest:updated"]

    if event_type not in allowed_events:
        logger.info(f"Ignoring event type: {event_type}")
        return {"status": "ignored", "reason": f"Event type: {event_type}"}

    # Parse payload
    payload = await request.json()

    # Extract PR info
    pr_info = extract_pr_info(payload)
    source_branch = pr_info["source_branch"]
    dest_branch = pr_info["dest_branch"]

    # Check branch patterns
    if not should_process_pr(source_branch, dest_branch):
        logger.info(f"Branch pattern not matched: {source_branch} -> {dest_branch}")
        return {
            "status": "ignored",
            "reason": f"Branch pattern not matched: {source_branch} -> {dest_branch}"
        }

    # Queue for background processing
    background_tasks.add_task(process_pr_review, pr_info)

    logger.info(
        f"PR #{pr_info['pr_id']} queued for review: {source_branch} -> {dest_branch}"
    )

    return {"status": "accepted", "pr_id": pr_info["pr_id"]}


@app.get("/health")
async def health_check() -> dict[str, str]:
    """
    Server health check endpoint.

    Returns:
        Health status dictionary
    """
    return {"status": "healthy", "service": "PR Code Review Automation"}


@app.get("/")
async def root() -> dict[str, str]:
    """
    Root endpoint.

    Returns:
        Service information dictionary
    """
    return {
        "message": "PR Code Review Automation Server",
        "health_endpoint": "/health",
        "webhook_endpoint": "/webhook"
    }
