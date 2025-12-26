"""Bitbucket REST API client for PR operations."""

import logging
import requests

from src.utils.retry import retry_with_backoff

logger = logging.getLogger(__name__)

BASE_URL = "https://api.bitbucket.org/2.0"


class BitbucketClient:
    """Client for interacting with Bitbucket REST API using API Token."""

    def __init__(self, email: str, api_token: str):
        """
        Initialize Bitbucket client.

        Args:
            email: Atlassian account email
            api_token: Bitbucket API token
        """
        self.email = email
        self.api_token = api_token
        # Basic Auth: email as username, API token as password
        self._auth = (email, api_token)

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def post_pr_comment(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        comment_text: str
    ) -> dict:
        """
        Post a general comment to a pull request.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID
            comment_text: Comment content in markdown

        Returns:
            API response as dictionary
        """
        url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"

        response = requests.post(
            url,
            auth=self._auth,
            headers={"Content-Type": "application/json"},
            json={
                "content": {
                    "raw": comment_text
                }
            },
            timeout=30
        )

        if not response.ok:
            logger.error(f"API Error: {response.status_code} - {response.text}")

        response.raise_for_status()

        logger.info(f"Comment posted to PR #{pr_id}")
        return response.json()

    @retry_with_backoff(max_retries=3, base_delay=1.0)
    def post_inline_comment(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int,
        file_path: str,
        line_number: int,
        comment_text: str
    ) -> dict:
        """
        Post an inline comment on a specific file and line.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID
            file_path: Path to the file
            line_number: Line number in the new file
            comment_text: Comment content

        Returns:
            API response as dictionary
        """
        url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/comments"

        response = requests.post(
            url,
            auth=self._auth,
            headers={"Content-Type": "application/json"},
            json={
                "content": {"raw": comment_text},
                "inline": {
                    "path": file_path,
                    "to": line_number
                }
            },
            timeout=30
        )
        response.raise_for_status()

        logger.info(f"Inline comment posted to {file_path}:{line_number}")
        return response.json()

    def get_pr_diff(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int
    ) -> str:
        """
        Get raw diff for a pull request.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            Raw diff content
        """
        url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diff"

        response = requests.get(url, auth=self._auth, timeout=60)
        response.raise_for_status()

        return response.text

    def get_pr_commits(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int
    ) -> list:
        """
        Get list of commits in a pull request.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            List of commit objects
        """
        url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/commits"

        response = requests.get(
            url,
            auth=self._auth,
            headers={"Accept": "application/json"},
            timeout=30
        )
        response.raise_for_status()

        return response.json().get("values", [])

    def get_pr_diffstat(
        self,
        workspace: str,
        repo_slug: str,
        pr_id: int
    ) -> list:
        """
        Get file change summary for a pull request.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            List of file change statistics
        """
        url = f"{BASE_URL}/repositories/{workspace}/{repo_slug}/pullrequests/{pr_id}/diffstat"

        response = requests.get(url, auth=self._auth, timeout=30)
        response.raise_for_status()

        return response.json().get("values", [])

    def get_clone_url(self, workspace: str, repo_slug: str) -> str:
        """
        Generate authenticated clone URL using API token.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug

        Returns:
            Authenticated HTTPS clone URL
        """
        return f"https://x-bitbucket-api-token-auth:{self.api_token}@bitbucket.org/{workspace}/{repo_slug}.git"
