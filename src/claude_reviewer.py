"""Claude integration for code review (API and CLI modes)."""

import logging
import os
import subprocess
from typing import List, Optional
from dataclasses import dataclass

from anthropic import Anthropic, AnthropicError

from src.git_operations import CommitInfo, ChangedFiles
from config.review_prompts import (
    get_review_prompt,
    get_comment_header,
    get_comment_footer
)

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = 300  # 5 minutes
MAX_DIFF_SIZE = 50000  # Characters
DEFAULT_MODEL = "claude-opus-4-5-20251101"  # Latest Opus model
MAX_TOKENS = 4096  # Maximum tokens for response


def get_review_language() -> str:
    """Get review language from environment variable."""
    return os.getenv("REVIEW_LANGUAGE", "tr")


def use_cli_mode() -> bool:
    """Check if CLI mode should be used instead of API."""
    return os.getenv("CLAUDE_USE_CLI", "false").lower() == "true"


@dataclass
class ReviewResult:
    """Data class for review result."""
    success: bool
    content: str
    error: Optional[str] = None


class ClaudeReviewer:
    """Handles code review using Claude API or CLI."""

    def __init__(self, working_dir: str, timeout: int = DEFAULT_TIMEOUT):
        """
        Initialize ClaudeReviewer.

        Args:
            working_dir: Directory containing the cloned repository
            timeout: Maximum time for execution in seconds
        """
        self.working_dir = working_dir
        self.timeout = timeout
        self.language = get_review_language()
        self.use_cli = use_cli_mode()

        # Initialize API client if not using CLI
        if not self.use_cli:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if not api_key:
                logger.error("ANTHROPIC_API_KEY not set! Set CLAUDE_USE_CLI=true to use CLI mode instead.")
                raise ValueError("ANTHROPIC_API_KEY environment variable is required for API mode")

            self.client = Anthropic(api_key=api_key)
            logger.info(f"Claude API mode initialized with model: {DEFAULT_MODEL}")
        else:
            self.client = None
            logger.info("Claude CLI mode initialized")

    def run_review(
        self,
        diff_content: str,
        commits: List[CommitInfo],
        changed_files: ChangedFiles
    ) -> ReviewResult:
        """
        Execute code review using Claude API or CLI.

        Args:
            diff_content: Raw diff content
            commits: List of commits in the PR
            changed_files: Categorized changed files

        Returns:
            ReviewResult with success status and content
        """
        # Prepare prompt with context
        prompt = self._build_prompt(diff_content, commits, changed_files)

        if self.use_cli:
            return self._run_cli_review(prompt)
        else:
            return self._run_api_review(prompt)

    def _run_api_review(self, prompt: str) -> ReviewResult:
        """
        Execute review using Anthropic API.

        Args:
            prompt: Review prompt

        Returns:
            ReviewResult with success status and content
        """
        try:
            logger.info(f"Sending review request to Claude API ({DEFAULT_MODEL})...")

            response = self.client.messages.create(
                model=DEFAULT_MODEL,
                max_tokens=MAX_TOKENS,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # Extract text content from response
            review_content = ""
            for block in response.content:
                if block.type == "text":
                    review_content += block.text

            if not review_content:
                logger.error("Empty response from Claude API")
                return ReviewResult(
                    success=False,
                    content="",
                    error="Empty response from Claude API"
                )

            logger.info("Review completed successfully via Claude API")
            return ReviewResult(
                success=True,
                content=review_content
            )

        except AnthropicError as e:
            logger.error(f"Claude API error: {e}")
            return ReviewResult(
                success=False,
                content="",
                error=f"Claude API error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Unexpected error during API review: {e}")
            return ReviewResult(
                success=False,
                content="",
                error=str(e)
            )

    def _run_cli_review(self, prompt: str) -> ReviewResult:
        """
        Execute review using Claude CLI (legacy mode).

        Args:
            prompt: Review prompt

        Returns:
            ReviewResult with success status and content
        """
        try:
            logger.info("Running review via Claude CLI...")

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
                logger.info("Review completed successfully via Claude CLI")
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
            logger.error(f"Unexpected error during CLI review: {e}")
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
