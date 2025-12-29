#!/usr/bin/env python3
"""Manual PR review trigger CLI tool."""

import argparse
import logging
import os
import sys

from src.bitbucket_client import BitbucketClient
from src.pr_processor import process_pr_review
from config.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


def validate_env_vars() -> tuple[str, str]:
    """
    Validate required environment variables.

    Returns:
        Tuple of (email, api_token)

    Raises:
        SystemExit: If required environment variables are missing
    """
    email = os.getenv("BITBUCKET_EMAIL")
    api_token = os.getenv("BITBUCKET_API_TOKEN")

    if not email or not api_token:
        logger.error("Missing required environment variables")
        print("\n❌ Error: Missing required environment variables")
        print("Please set the following environment variables:")
        print("  - BITBUCKET_EMAIL")
        print("  - BITBUCKET_API_TOKEN")
        sys.exit(1)

    return email, api_token


def trigger_review(workspace: str, repo_slug: str, pr_id: int) -> None:
    """
    Trigger manual PR review.

    Args:
        workspace: Bitbucket workspace slug
        repo_slug: Repository slug
        pr_id: Pull request ID
    """
    try:
        logger.info(f"Starting manual review for PR #{pr_id}")
        print(f"\n🔍 Fetching PR information for #{pr_id}...")

        # Get credentials
        email, api_token = validate_env_vars()

        # Initialize Bitbucket client
        client = BitbucketClient(email, api_token)

        # Fetch PR information
        pr_info = client.get_pr_info(workspace, repo_slug, pr_id)

        print(f"✅ PR Info Retrieved:")
        print(f"   Title: {pr_info['title']}")
        print(f"   Author: {pr_info['author']}")
        print(f"   Source: {pr_info['source_branch']}")
        print(f"   Destination: {pr_info['dest_branch']}\n")

        # Trigger review process
        print("🚀 Starting review process...")
        process_pr_review(pr_info)

        print("\n✅ Review completed successfully!")
        logger.info(f"Manual review completed for PR #{pr_id}")

    except Exception as e:
        logger.error(f"Failed to trigger review: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Manually trigger PR code review",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --workspace myworkspace --repo myrepo --pr-id 123
  %(prog)s -w myworkspace -r myrepo -p 123

Environment Variables:
  BITBUCKET_EMAIL        Atlassian account email
  BITBUCKET_API_TOKEN    Bitbucket API token
        """
    )

    parser.add_argument(
        "-w", "--workspace",
        required=True,
        help="Bitbucket workspace slug"
    )

    parser.add_argument(
        "-r", "--repo",
        required=True,
        help="Repository slug"
    )

    parser.add_argument(
        "-p", "--pr-id",
        type=int,
        required=True,
        help="Pull request ID"
    )

    args = parser.parse_args()

    # Trigger the review
    trigger_review(args.workspace, args.repo, args.pr_id)


if __name__ == "__main__":
    main()
