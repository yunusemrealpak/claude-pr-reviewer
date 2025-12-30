#!/usr/bin/env python3
"""
Gmail OAuth2 Setup Tool

This script helps you generate the refresh token needed for Gmail API authentication.
Run this once to get your OAuth2 credentials, then add them to .env file.
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path to import from config
sys.path.insert(0, str(Path(__file__).parent.parent))

from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scope for sending emails
SCOPES = ['https://www.googleapis.com/auth/gmail.send']


def create_credentials_json():
    """
    Interactive credential creation.

    Asks user for Client ID and Client Secret from Google Cloud Console.
    """
    print("\n" + "="*60)
    print("Gmail OAuth2 Setup - Step 1: Get Client Credentials")
    print("="*60)
    print("\nBefore running this script, you need to:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create a new project (or select existing)")
    print("3. Enable Gmail API:")
    print("   - Go to 'APIs & Services' > 'Library'")
    print("   - Search for 'Gmail API' and click 'Enable'")
    print("4. Create OAuth2 credentials:")
    print("   - Go to 'APIs & Services' > 'Credentials'")
    print("   - Click 'Create Credentials' > 'OAuth client ID'")
    print("   - Application type: 'Desktop app'")
    print("   - Name: 'PR Review Bot' (or any name)")
    print("   ⚠️  IMPORTANT: Add these Authorized redirect URIs:")
    print("      - http://localhost:8080/")
    print("      - http://localhost:8080")
    print("   - Click 'Create'")
    print("5. Copy the Client ID and Client Secret")
    print("\n" + "="*60)

    client_id = input("\nEnter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()

    if not client_id or not client_secret:
        print("\n❌ Error: Client ID and Client Secret are required!")
        sys.exit(1)

    # Create credentials JSON structure
    credentials = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "redirect_uris": ["http://localhost:8080/", "http://localhost:8080"]
        }
    }

    # Save to temporary file
    creds_file = Path(__file__).parent / "credentials.json"
    with open(creds_file, 'w') as f:
        json.dump(credentials, f, indent=2)

    print(f"\n✅ Credentials saved to: {creds_file}")
    return creds_file


def get_refresh_token(credentials_file):
    """
    Run OAuth2 flow to get refresh token.

    Args:
        credentials_file: Path to credentials.json file

    Returns:
        Refresh token string
    """
    print("\n" + "="*60)
    print("Gmail OAuth2 Setup - Step 2: Authorization")
    print("="*60)
    print("\nThis will open your browser for Google authorization.")
    print("Please sign in and grant access to send emails.\n")

    try:
        # Run OAuth flow
        flow = InstalledAppFlow.from_client_secrets_file(
            str(credentials_file),
            SCOPES
        )

        # This will open browser automatically
        # Using fixed port 8080 - make sure this is added to Google Cloud Console
        creds = flow.run_local_server(port=8080)

        if not creds or not creds.refresh_token:
            print("\n❌ Error: Failed to get refresh token!")
            sys.exit(1)

        return creds.refresh_token, creds.client_id, creds.client_secret

    except Exception as e:
        print(f"\n❌ Error during authorization: {e}")
        print("\nTroubleshooting:")
        print("- Make sure you have a web browser installed")
        print("- Check that your Client ID and Client Secret are correct")
        print("- Verify that Gmail API is enabled in Google Cloud Console")
        sys.exit(1)


def save_to_env(client_id, client_secret, refresh_token, sender_email):
    """
    Display instructions for adding to .env file.

    Args:
        client_id: OAuth2 client ID
        client_secret: OAuth2 client secret
        refresh_token: OAuth2 refresh token
        sender_email: Email address that will send notifications
    """
    print("\n" + "="*60)
    print("Gmail OAuth2 Setup - Step 3: Update .env File")
    print("="*60)
    print("\n✅ Authorization successful!")
    print("\nAdd these lines to your .env file:")
    print("\n" + "-"*60)
    print(f"""
# Email Configuration
EMAIL_ENABLED=true
EMAIL_PROVIDER=gmail
EMAIL_SENDER_ADDRESS={sender_email}
EMAIL_OAUTH_CLIENT_ID={client_id}
EMAIL_OAUTH_CLIENT_SECRET={client_secret}
EMAIL_OAUTH_REFRESH_TOKEN={refresh_token}
EMAIL_FIXED_RECIPIENT=your-recipient@example.com
""")
    print("-"*60)
    print("\n⚠️  Important:")
    print("- Replace 'your-recipient@example.com' with actual recipient email")
    print("- Keep these credentials secure!")
    print("- Add .env to .gitignore to prevent committing secrets")
    print("\n✅ Setup complete! You can now send emails via Gmail API.")


def main():
    """Main setup flow."""
    print("""
╔══════════════════════════════════════════════════════════╗
║         Gmail OAuth2 Setup for PR Review Bot            ║
║                                                          ║
║  This tool will help you configure Gmail API access     ║
║  for sending email notifications.                       ║
╚══════════════════════════════════════════════════════════╝
    """)

    # Step 1: Get Client ID and Secret
    creds_file = create_credentials_json()

    # Step 2: Get sender email
    print("\n" + "="*60)
    sender_email = input("Enter the Gmail address that will SEND notifications: ").strip()
    if not sender_email or '@' not in sender_email:
        print("\n❌ Error: Valid email address is required!")
        sys.exit(1)

    # Step 3: Run OAuth flow
    refresh_token, client_id, client_secret = get_refresh_token(creds_file)

    # Step 4: Display .env instructions
    save_to_env(client_id, client_secret, refresh_token, sender_email)

    # Cleanup
    try:
        creds_file.unlink()
        print(f"\n🗑️  Cleaned up temporary file: {creds_file}")
    except:
        pass


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(1)
