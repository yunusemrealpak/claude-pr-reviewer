"""Notification utilities for PR review failures."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.bitbucket_client import BitbucketClient

logger = logging.getLogger(__name__)


def notify_review_failure(
    client: "BitbucketClient",
    workspace: str,
    repo_slug: str,
    pr_id: int,
    error: Exception
) -> None:
    """
    Send notification when review process fails.

    Posts an error comment to the PR informing about the failure.

    Args:
        client: BitbucketClient instance for API calls
        workspace: Bitbucket workspace slug
        repo_slug: Repository slug
        pr_id: Pull request ID
        error: The exception that caused the failure
    """
    error_comment = f"""## Automatic Review Failed

An error occurred while processing this PR:
```
{str(error)[:500]}
```

Please request a manual review or contact the automation team."""

    try:
        client.post_pr_comment(workspace, repo_slug, pr_id, error_comment)
        logger.info(f"Failure notification posted to PR #{pr_id}")
    except Exception as e:
        logger.error(f"Failed to post failure notification: {e}")

    # Log error for alerting systems
    logger.error(
        f"PR Review Failed - PR #{pr_id}",
        extra={
            "pr_id": pr_id,
            "workspace": workspace,
            "repo_slug": repo_slug,
            "error": str(error),
            "error_type": type(error).__name__
        }
    )


def notify_clone_failure(
    client: "BitbucketClient",
    workspace: str,
    repo_slug: str,
    pr_id: int
) -> None:
    """
    Send notification when repository clone fails.

    Args:
        client: BitbucketClient instance for API calls
        workspace: Bitbucket workspace slug
        repo_slug: Repository slug
        pr_id: Pull request ID
    """
    comment = """## Automatic Review Failed

Repository could not be cloned. Please request a manual review."""

    try:
        client.post_pr_comment(workspace, repo_slug, pr_id, comment)
    except Exception as e:
        logger.error(f"Failed to post clone failure notification: {e}")


def notify_no_changes(
    client: "BitbucketClient",
    workspace: str,
    repo_slug: str,
    pr_id: int
) -> None:
    """
    Send notification when no reviewable changes are found.

    Args:
        client: BitbucketClient instance for API calls
        workspace: Bitbucket workspace slug
        repo_slug: Repository slug
        pr_id: Pull request ID
    """
    comment = """## Automatic Review Notice

No Dart file changes were found in this PR."""

    try:
        client.post_pr_comment(workspace, repo_slug, pr_id, comment)
    except Exception as e:
        logger.error(f"Failed to post no-changes notification: {e}")
