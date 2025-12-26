"""PR review processing logic."""

import logging
import os
from dataclasses import dataclass
from typing import Optional

from src.bitbucket_client import BitbucketClient
from src.git_operations import GitOperations
from src.claude_reviewer import ClaudeReviewer, format_review_comment
from src.utils.notifications import (
    notify_review_failure,
    notify_clone_failure,
    notify_no_changes
)

logger = logging.getLogger(__name__)


@dataclass
class PRInfo:
    """Data class for PR information."""
    pr_id: int
    workspace: str
    repo_slug: str
    source_branch: str
    dest_branch: str
    title: str
    author: str


class PRProcessor:
    """Handles the complete PR review workflow."""

    def __init__(self):
        """Initialize PRProcessor with required clients."""
        email = os.getenv("BITBUCKET_EMAIL", "")
        api_token = os.getenv("BITBUCKET_API_TOKEN", "")

        self.bitbucket = BitbucketClient(email, api_token)
        self.git_ops: Optional[GitOperations] = None

    def process(self, pr_info: PRInfo) -> bool:
        """
        Execute the full PR review workflow.

        Args:
            pr_info: PR information data

        Returns:
            True if review completed successfully, False otherwise
        """
        logger.info(f"Starting review for PR #{pr_info.pr_id}")

        self.git_ops = GitOperations()

        try:
            # Step 1: Clone repository
            clone_url = self.bitbucket.get_clone_url(
                pr_info.workspace,
                pr_info.repo_slug
            )

            if not self.git_ops.clone_repository(clone_url, pr_info.source_branch):
                notify_clone_failure(
                    self.bitbucket,
                    pr_info.workspace,
                    pr_info.repo_slug,
                    pr_info.pr_id
                )
                return False

            # Step 2: Get PR context
            commits = self.git_ops.get_commits(pr_info.dest_branch)
            changed_files = self.git_ops.get_changed_files(pr_info.dest_branch)
            diff_content = self.git_ops.get_diff_content(pr_info.dest_branch)

            if not diff_content:
                logger.warning("No diff content found")
                notify_no_changes(
                    self.bitbucket,
                    pr_info.workspace,
                    pr_info.repo_slug,
                    pr_info.pr_id
                )
                return False

            # Step 3: Run Claude review
            reviewer = ClaudeReviewer(self.git_ops.working_directory)
            result = reviewer.run_review(diff_content, commits, changed_files)

            if not result.success:
                self._post_error_comment(pr_info, result.error or "Unknown error")
                return False

            # Step 4: Post review comment
            formatted_comment = format_review_comment(result.content)
            self.bitbucket.post_pr_comment(
                pr_info.workspace,
                pr_info.repo_slug,
                pr_info.pr_id,
                formatted_comment
            )

            logger.info(f"Review completed for PR #{pr_info.pr_id}")
            return True

        except Exception as e:
            logger.exception(f"Error processing PR: {e}")
            notify_review_failure(
                self.bitbucket,
                pr_info.workspace,
                pr_info.repo_slug,
                pr_info.pr_id,
                e
            )
            return False

        finally:
            self._cleanup()

    def _post_error_comment(self, pr_info: PRInfo, error_message: str) -> None:
        """Post an error comment to the PR."""
        comment = f"""## Automatic Review Failed

An error occurred during code review:
```
{error_message[:500]}
```

Please request a manual review."""

        try:
            self.bitbucket.post_pr_comment(
                pr_info.workspace,
                pr_info.repo_slug,
                pr_info.pr_id,
                comment
            )
        except Exception as e:
            logger.error(f"Failed to post error comment: {e}")

    def _cleanup(self) -> None:
        """Clean up resources."""
        if self.git_ops:
            self.git_ops.cleanup()
            self.git_ops = None


def process_pr_review(pr_info_dict: dict) -> None:
    """
    Background task entry point for PR review.

    Args:
        pr_info_dict: Dictionary containing PR information
    """
    pr_info = PRInfo(
        pr_id=pr_info_dict["pr_id"],
        workspace=pr_info_dict["workspace"],
        repo_slug=pr_info_dict["repo_slug"],
        source_branch=pr_info_dict["source_branch"],
        dest_branch=pr_info_dict["dest_branch"],
        title=pr_info_dict.get("title", ""),
        author=pr_info_dict.get("author", "Unknown")
    )

    processor = PRProcessor()
    processor.process(pr_info)
