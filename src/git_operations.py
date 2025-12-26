"""Git operations for repository cloning and diff extraction."""

import logging
import subprocess
import tempfile
import shutil
from typing import Optional, Dict, List
from dataclasses import dataclass

from git import Repo
from git.exc import GitCommandError

logger = logging.getLogger(__name__)


@dataclass
class CommitInfo:
    """Data class for commit information."""
    sha: str
    message: str
    author: str
    files: List[str]


@dataclass
class ChangedFiles:
    """Data class for changed files categorization."""
    added: List[str]
    modified: List[str]
    deleted: List[str]


class GitOperations:
    """Handles Git operations for PR review."""

    def __init__(self):
        """Initialize GitOperations."""
        self.temp_dir: Optional[str] = None
        self.repo: Optional[Repo] = None

    def clone_repository(self, clone_url: str, branch: str) -> bool:
        """
        Clone repository to temporary directory and checkout branch.

        Args:
            clone_url: Authenticated Git clone URL
            branch: Branch name to checkout

        Returns:
            True if successful, False otherwise
        """
        self.temp_dir = tempfile.mkdtemp(prefix="pr_review_")

        try:
            logger.info(f"Cloning repository to {self.temp_dir}")
            self.repo = Repo.clone_from(clone_url, self.temp_dir)

            # Fetch all remote branches
            self.repo.remotes.origin.fetch()

            # Checkout the PR source branch
            self.repo.git.checkout(f"origin/{branch}")

            logger.info(f"Successfully checked out branch: {branch}")
            return True

        except GitCommandError as e:
            logger.error(f"Git error: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during clone: {e}")
            return False

    def get_commits(self, dest_branch: str) -> List[CommitInfo]:
        """
        Get commits that are in HEAD but not in destination branch.

        Args:
            dest_branch: Destination branch name

        Returns:
            List of CommitInfo objects
        """
        commits = []
        try:
            for commit in self.repo.iter_commits(f"origin/{dest_branch}..HEAD"):
                commits.append(CommitInfo(
                    sha=commit.hexsha[:8],
                    message=commit.summary,
                    author=commit.author.name,
                    files=list(commit.stats.files.keys())
                ))
            logger.info(f"Found {len(commits)} commits")
        except Exception as e:
            logger.error(f"Error getting commits: {e}")
        return commits

    def get_changed_files(self, dest_branch: str) -> ChangedFiles:
        """
        Get categorized list of changed files.

        Args:
            dest_branch: Destination branch name

        Returns:
            ChangedFiles object with added, modified, and deleted files
        """
        try:
            dest_commit = self.repo.commit(f"origin/{dest_branch}")
            head_commit = self.repo.head.commit
            diff = dest_commit.diff(head_commit)

            return ChangedFiles(
                added=[d.b_path for d in diff.iter_change_type("A")],
                modified=[d.a_path for d in diff.iter_change_type("M")],
                deleted=[d.a_path for d in diff.iter_change_type("D")]
            )
        except Exception as e:
            logger.error(f"Error getting changed files: {e}")
            return ChangedFiles(added=[], modified=[], deleted=[])

    def get_diff_content(self, dest_branch: str, file_pattern: str = "*.dart") -> str:
        """
        Get unified diff content for specified file pattern.

        Args:
            dest_branch: Destination branch name
            file_pattern: Glob pattern for files to include in diff

        Returns:
            Raw diff content as string
        """
        try:
            result = subprocess.run(
                [
                    "git", "diff",
                    f"origin/{dest_branch}...HEAD",
                    "--", file_pattern
                ],
                cwd=self.temp_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            return result.stdout
        except subprocess.TimeoutExpired:
            logger.error("Diff command timed out")
            return ""
        except Exception as e:
            logger.error(f"Error getting diff: {e}")
            return ""

    def get_file_content(self, file_path: str) -> Optional[str]:
        """
        Read content of a file from the repository.

        Args:
            file_path: Relative path to file

        Returns:
            File content or None if not found
        """
        if not self.temp_dir:
            return None

        full_path = f"{self.temp_dir}/{file_path}"
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"File not found: {file_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None

    @property
    def working_directory(self) -> Optional[str]:
        """Get the temporary working directory path."""
        return self.temp_dir

    def cleanup(self) -> None:
        """Remove temporary directory and clean up resources."""
        if self.temp_dir and shutil.os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            logger.info("Temporary directory cleaned up")
            self.temp_dir = None
            self.repo = None
