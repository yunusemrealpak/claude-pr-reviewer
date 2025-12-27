"""Claude Code CLI integration for code review."""

import logging
import os
import subprocess
from typing import List, Optional
from dataclasses import dataclass

from src.git_operations import CommitInfo, ChangedFiles
from config.review_prompts import (
    get_review_prompt,
    get_comment_header,
    get_comment_footer
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_DIFF_SIZE = 50000  # Characters


def get_review_language() -> str:
    """Get review language from environment variable."""
    return os.getenv("REVIEW_LANGUAGE", "tr")


@dataclass
class ReviewResult:
    """Data class for review result."""
    success: bool
    content: str
    error: Optional[str] = None


class ClaudeReviewer:
    """Handles code review using Claude Code CLI."""

    def __init__(self, working_dir: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize ClaudeReviewer.

        Args:
            working_dir: Directory containing the cloned repository
            timeout: Maximum time for Claude CLI execution in seconds
        """
        self.working_dir = working_dir
        self.timeout = timeout
        self.language = get_review_language()

    def run_review(
        self,
        diff_content: str,
        commits: List[CommitInfo],
        changed_files: ChangedFiles
    ) -> ReviewResult:
        """
        Execute code review using Claude Code CLI.

        Args:
            diff_content: Raw diff content
            commits: List of commits in the PR
            changed_files: Categorized changed files

        Returns:
            ReviewResult with success status and content
        """
        # Prepare prompt with context
        prompt = self._build_prompt(diff_content, commits, changed_files)

        try:
            result = subprocess.run(
                [
                    "claude",
                    "-p", prompt,
                    "--output-format", "text",
                    "--allowedTools", "Read,Grep",
                    "--max-turns", "3"
                ],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=self.working_dir
            )

            if result.returncode == 0:
                return ReviewResult(
                    success=True,
                    content=result.stdout
                )
            else:
                logger.error(f"Claude CLI error: {result.stderr}")
                return ReviewResult(
                    success=False,
                    content="",
                    error=result.stderr
                )

        except subprocess.TimeoutExpired:
            logger.error("Claude CLI timed out")
            return ReviewResult(
                success=False,
                content="",
                error="Code review timed out. Please request manual review."
            )
        except FileNotFoundError:
            logger.error("Claude CLI not found")
            return ReviewResult(
                success=False,
                content="",
                error="Claude CLI is not installed. Install: npm install -g @anthropic-ai/claude-code"
            )
        except Exception as e:
            logger.error(f"Unexpected error during review: {e}")
            return ReviewResult(
                success=False,
                content="",
                error=str(e)
            )

    def _build_prompt(
        self,
        diff_content: str,
        commits: List[CommitInfo],
        changed_files: ChangedFiles
    ) -> str:
        """
        Build the review prompt with context.

        Args:
            diff_content: Raw diff content
            commits: List of commits in the PR
            changed_files: Categorized changed files

        Returns:
            Formatted prompt string
        """
        # Build commit summary
        commit_summary = "\n".join([
            f"- {c.sha}: {c.message} (by {c.author})"
            for c in commits
        ])

        # Build files summary
        files_summary = (
            f"Added: {len(changed_files.added)}, "
            f"Modified: {len(changed_files.modified)}, "
            f"Deleted: {len(changed_files.deleted)}"
        )

        # Truncate diff if too large
        truncated_diff = diff_content[:MAX_DIFF_SIZE]
        if len(diff_content) > MAX_DIFF_SIZE:
            truncated_diff += "\n\n... (diff truncated due to size)"

        # Get the review prompt template with language
        return get_review_prompt(
            commit_summary,
            files_summary,
            truncated_diff,
            self.language
        )


def format_review_comment(review_text: str, language: str = None) -> str:
    """
    Format review result as a PR comment.

    Args:
        review_text: Raw review text from Claude
        language: Language code (tr/en), defaults to env variable

    Returns:
        Formatted markdown comment
    """
    if language is None:
        language = get_review_language()

    header = get_comment_header(language)
    footer = get_comment_footer(language)

    return f"""{header}

{review_text}

---
{footer}"""
