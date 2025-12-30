"""Email notification service using Gmail API with OAuth2."""

import base64
import logging
import os
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from config.email_templates import get_email_subject, get_email_body

logger = logging.getLogger(__name__)


@dataclass
class EmailConfig:
    """Email configuration using OAuth2 credentials."""

    enabled: bool
    provider: str  # 'gmail' or 'outlook'
    client_id: str
    client_secret: str
    refresh_token: str
    sender_address: str
    fixed_recipient: str

    @staticmethod
    def from_env() -> Optional["EmailConfig"]:
        """
        Load email configuration from environment variables.

        Returns:
            EmailConfig if email is enabled and configured, None otherwise
        """
        # Check if email notifications are enabled
        enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
        if not enabled:
            logger.info("Email notifications are disabled (EMAIL_ENABLED=false)")
            return None

        # Get provider
        provider = os.getenv("EMAIL_PROVIDER", "gmail").lower()
        if provider not in ["gmail", "outlook"]:
            logger.error(f"Invalid EMAIL_PROVIDER: {provider}. Currently only 'gmail' is supported for OAuth2")
            return None

        # Get OAuth2 credentials
        client_id = os.getenv("EMAIL_OAUTH_CLIENT_ID", "")
        client_secret = os.getenv("EMAIL_OAUTH_CLIENT_SECRET", "")
        refresh_token = os.getenv("EMAIL_OAUTH_REFRESH_TOKEN", "")
        sender_address = os.getenv("EMAIL_SENDER_ADDRESS", "")
        fixed_recipient = os.getenv("EMAIL_FIXED_RECIPIENT", "")

        # Validate required fields
        if not all([client_id, client_secret, refresh_token, sender_address, fixed_recipient]):
            logger.error(
                "Email OAuth2 configuration incomplete. Required: "
                "EMAIL_OAUTH_CLIENT_ID, EMAIL_OAUTH_CLIENT_SECRET, "
                "EMAIL_OAUTH_REFRESH_TOKEN, EMAIL_SENDER_ADDRESS, EMAIL_FIXED_RECIPIENT"
            )
            return None

        return EmailConfig(
            enabled=True,
            provider=provider,
            client_id=client_id,
            client_secret=client_secret,
            refresh_token=refresh_token,
            sender_address=sender_address,
            fixed_recipient=fixed_recipient
        )


class EmailService:
    """Service for sending email notifications using Gmail API with OAuth2."""

    def __init__(self):
        """Initialize email service with OAuth2 configuration."""
        self.config = EmailConfig.from_env()
        if self.config:
            logger.info(f"Email service initialized with OAuth2 provider: {self.config.provider}")
        else:
            logger.info("Email service disabled due to missing or invalid configuration")

    @staticmethod
    def build_pr_url(workspace: str, repo_slug: str, pr_id: int) -> str:
        """
        Build Bitbucket PR URL.

        Args:
            workspace: Bitbucket workspace slug
            repo_slug: Repository slug
            pr_id: Pull request ID

        Returns:
            Full Bitbucket PR URL
        """
        return f"https://bitbucket.org/{workspace}/{repo_slug}/pull-requests/{pr_id}"

    def _get_gmail_service(self):
        """
        Create Gmail API service with OAuth2 credentials.

        Returns:
            Gmail API service object

        Raises:
            Exception: If OAuth2 authentication fails
        """
        try:
            # Create credentials from refresh token
            creds = Credentials(
                token=None,
                refresh_token=self.config.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.config.client_id,
                client_secret=self.config.client_secret,
                scopes=["https://www.googleapis.com/auth/gmail.send"]
            )

            # Refresh the access token
            creds.refresh(Request())

            # Build Gmail API service
            service = build("gmail", "v1", credentials=creds)
            return service

        except Exception as e:
            logger.error(f"Failed to create Gmail service: {e}")
            raise

    def _create_message(self, to: str, subject: str, body: str) -> dict:
        """
        Create email message in Gmail API format.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body text

        Returns:
            Gmail API message object
        """
        # Create MIME message
        message = MIMEMultipart()
        message["To"] = to
        message["From"] = self.config.sender_address
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain", "utf-8"))

        # Encode message to base64
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        return {"raw": raw_message}

    def _send_gmail_message(self, recipient: str, subject: str, body: str) -> bool:
        """
        Send email using Gmail API.

        Args:
            recipient: Email recipient address
            subject: Email subject
            body: Email body text

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.config:
            logger.debug("Email not sent: service not configured")
            return False

        try:
            # Get Gmail service
            service = self._get_gmail_service()

            # Create message
            message = self._create_message(recipient, subject, body)

            # Send message
            result = service.users().messages().send(
                userId="me",
                body=message
            ).execute()

            logger.info(f"Email sent successfully to {recipient} (Message ID: {result.get('id')})")
            return True

        except HttpError as e:
            logger.error(f"Gmail API HTTP error: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send email via Gmail API: {e}")
            return False

    def send_review_notification(
        self,
        pr_info,
        language: str = "tr"
    ) -> bool:
        """
        Send PR review notification email.

        Args:
            pr_info: PRInfo object containing PR details
            language: Language for email template (tr/en)

        Returns:
            True if email sent successfully, False otherwise
        """
        if not self.config:
            logger.debug("Email notification skipped: service not configured")
            return False

        try:
            # Build PR URL
            pr_url = self.build_pr_url(
                pr_info.workspace,
                pr_info.repo_slug,
                pr_info.pr_id
            )

            # Generate email content
            subject = get_email_subject(pr_info.title, language)
            body = get_email_body(
                pr_title=pr_info.title,
                pr_author=pr_info.author,
                pr_url=pr_url,
                language=language
            )

            # Send email based on provider
            if self.config.provider == "gmail":
                success = self._send_gmail_message(
                    recipient=self.config.fixed_recipient,
                    subject=subject,
                    body=body
                )
            else:
                logger.error(f"Provider '{self.config.provider}' not yet implemented for OAuth2")
                return False

            if success:
                logger.info(f"PR review notification sent for PR #{pr_info.pr_id}")
            else:
                logger.warning(f"Failed to send PR review notification for PR #{pr_info.pr_id}")

            return success

        except Exception as e:
            logger.error(f"Error sending review notification: {e}")
            return False
