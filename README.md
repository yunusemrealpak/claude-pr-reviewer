# Bitbucket PR Code Review Automation

Automated code review system for Bitbucket Cloud pull requests using **Claude Opus 4.5** via Anthropic API.

## Features

- Webhook-based PR detection for `feature/*` and `fix/*` branches
- Manual PR review trigger via CLI tool (for missed PRs when server is offline)
- Automatic repository cloning and diff extraction
- AI-powered code review using **Claude Opus 4.5** via Anthropic API
- Flutter/Dart focused review criteria (Clean Architecture, BLoC/Cubit patterns)
- Automatic PR comment posting with review results
- Multi-language support (Turkish & English)
- Email notifications with PR links (Gmail OAuth2)
- Dual mode: API (default) or CLI

## Architecture

```
Bitbucket PR → Webhook → FastAPI Server → Clone Repo → Claude API (Opus 4.5) → PR Comment + Email
```

## Requirements

- Python 3.10+
- **Anthropic API Key** (for Claude API access)
- ngrok or cloudflared (for webhook tunneling)
- Bitbucket Cloud account with API token
- (Optional) Claude CLI for CLI mode

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/claude-pr-reviewer.git
cd claude-pr-reviewer
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your credentials:

```env
BITBUCKET_EMAIL=your-email@example.com
BITBUCKET_API_TOKEN=your-api-token
WEBHOOK_SECRET=your-webhook-secret

# Claude Configuration
CLAUDE_USE_CLI=false
ANTHROPIC_API_KEY=sk-ant-api03-your-api-key

# Email notifications (optional - run setup script first)
EMAIL_ENABLED=true
EMAIL_PROVIDER=gmail
EMAIL_SENDER_ADDRESS=your-email@gmail.com
EMAIL_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
EMAIL_OAUTH_CLIENT_SECRET=your-client-secret
EMAIL_OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_FIXED_RECIPIENT=team-lead@company.com
```

### 5. Get Anthropic API Key

1. Go to [Anthropic Console](https://console.anthropic.com/)
2. Sign in or create an account
3. Navigate to **API Keys**
4. Click **Create Key**
5. Copy the API key (starts with `sk-ant-api03-`)
6. Add to `.env`:
   ```env
   ANTHROPIC_API_KEY=sk-ant-api03-your-api-key
   ```

**Note:** The system uses Claude Opus 4.5 model by default for high-quality code reviews.

### 5b. (Optional) Use Claude CLI Instead

If you prefer to use Claude CLI instead of API:

1. Install Claude CLI:
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. Authenticate:
   ```bash
   claude auth login
   ```

3. Set in `.env`:
   ```env
   CLAUDE_USE_CLI=true
   ```

### 6. Start the server

```bash
python main.py
```

### 7. Start ngrok tunnel

```bash
ngrok http 8000
```

### 8. Configure Bitbucket Webhook

1. Go to Repository Settings → Webhooks
2. Add webhook:
   - **URL**: `https://your-ngrok-url.ngrok-free.app/webhook`
   - **Secret**: Same as `WEBHOOK_SECRET` in `.env`
   - **Triggers**: Select both:
     - `Pull Request: Created`
     - `Pull Request: Updated`

## Bitbucket API Token Setup

1. Go to **Personal Settings** → **API tokens**
2. Create token with scopes:
   - `read:repository:bitbucket`
   - `read:pullrequest:bitbucket`
   - `write:pullrequest:bitbucket`

## Email Notification Setup (Optional)

Email notifications send a brief message with a PR link after each review is completed using **Gmail API with OAuth2** authentication.

### Quick Setup (Automated Script)

Run the interactive setup script to configure Gmail OAuth2:

```bash
python tools/setup_gmail_oauth.py
```

This script will:
1. Ask for your Google Cloud Console Client ID and Client Secret
2. Open a browser for Google authorization
3. Generate a refresh token
4. Provide configuration to add to your `.env` file

### Manual Setup

If you prefer manual setup:

#### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Project name: "PR Review Automation" (or any name)

#### Step 2: Enable Gmail API

1. In Google Cloud Console, go to **APIs & Services** → **Library**
2. Search for "Gmail API"
3. Click **Enable**

#### Step 3: Create OAuth2 Credentials

1. Go to **APIs & Services** → **Credentials**
2. Click **Create Credentials** → **OAuth client ID**
3. If asked, configure OAuth consent screen:
   - User Type: **External**
   - App name: "PR Review Bot"
   - Add your email as developer contact
   - Save and continue
4. Back to credentials creation:
   - Application type: **Desktop app**
   - Name: "PR Review Bot"
   - ⚠️ **IMPORTANT:** Add **Authorized redirect URIs**:
     - `http://localhost:8080/`
     - `http://localhost:8080`
   - Click **Create**
5. **Copy the Client ID and Client Secret** (you'll need these)

#### Step 4: Get Refresh Token

Run the setup script:
```bash
python tools/setup_gmail_oauth.py
```

Or manually use Google OAuth Playground:
1. Go to [OAuth 2.0 Playground](https://developers.google.com/oauthplayground/)
2. Click settings icon (⚙️) → Check "Use your own OAuth credentials"
3. Enter your Client ID and Client Secret
4. In Step 1: Select `https://www.googleapis.com/auth/gmail.send`
5. Click "Authorize APIs" and sign in
6. In Step 2: Click "Exchange authorization code for tokens"
7. Copy the **Refresh token**

#### Step 5: Update .env File

Add these to your `.env`:
```env
EMAIL_ENABLED=true
EMAIL_PROVIDER=gmail
EMAIL_SENDER_ADDRESS=your-email@gmail.com
EMAIL_OAUTH_CLIENT_ID=your-client-id.apps.googleusercontent.com
EMAIL_OAUTH_CLIENT_SECRET=your-client-secret
EMAIL_OAUTH_REFRESH_TOKEN=your-refresh-token
EMAIL_FIXED_RECIPIENT=team-lead@company.com
```

### Disable Email Notifications

Set `EMAIL_ENABLED=false` in `.env` to disable email notifications.

### Troubleshooting

**"400: redirect_uri_mismatch" error:**
- Go to Google Cloud Console → Credentials
- Click on your OAuth Client ID
- Under "Authorized redirect URIs", add:
  - `http://localhost:8080/`
  - `http://localhost:8080`
- Click **Save** and try again

**"OAuth2 authentication failed":**
- Verify Client ID and Client Secret are correct
- Ensure Gmail API is enabled in Google Cloud Console
- Check refresh token is valid (regenerate if needed)

**"Invalid grant" error:**
- Refresh token may have expired
- Run `python tools/setup_gmail_oauth.py` again to get a new token

**Email not received:**
- Check spam/junk folder
- Verify `EMAIL_FIXED_RECIPIENT` address is correct
- Check server logs for error messages
- Ensure sender email matches the Google account used for OAuth

**"Access blocked" during authorization:**
- Your app is not verified by Google (expected for personal use)
- Click "Advanced" → "Go to [Your App Name] (unsafe)"
- This is safe if you created the app yourself

**Note:** Email failures do not block the PR review process. If email sending fails, the error is logged and the review continues normally.

## Project Structure

```
├── main.py                 # Entry point (server)
├── src/
│   ├── server.py           # FastAPI webhook handler
│   ├── pr_processor.py     # PR review orchestrator
│   ├── bitbucket_client.py # Bitbucket API client
│   ├── git_operations.py   # Git operations
│   ├── claude_reviewer.py  # Claude CLI integration
│   ├── trigger_review.py   # Manual PR review trigger CLI
│   └── utils/
│       ├── retry.py        # Retry decorator
│       └── notifications.py
├── config/
│   ├── logging_config.py
│   └── review_prompts.py
└── requirements.txt
```

## Manual PR Review Trigger

If the server is offline when a PR is created, you can manually trigger the review using the CLI tool:

```bash
python -m src.trigger_review --workspace <workspace> --repo <repo-slug> --pr-id <pr-id>
```

**Example:**
```bash
python -m src.trigger_review --workspace mycompany --repo mobile-app --pr-id 123
```

**Short form:**
```bash
python -m src.trigger_review -w mycompany -r mobile-app -p 123
```

**Requirements:**
- Environment variables must be set (`BITBUCKET_EMAIL`, `BITBUCKET_API_TOKEN`)
- The tool will fetch PR information from Bitbucket API and trigger the same review process

**Help:**
```bash
python -m src.trigger_review --help
```

## How It Works

### Automatic (Webhook-based)

1. PR is created or updated from `feature/*` or `fix/*` to `development`
2. Bitbucket sends webhook to your server
3. Server clones the repository to temp directory
4. Extracts diff for Dart files
5. Sends diff to **Claude Opus 4.5** via Anthropic API for review
6. Posts review comment back to PR
7. Sends email notification with PR link
8. Cleans up temp directory

### Manual Trigger

1. Run `python -m src.trigger_review` with PR information
2. Tool fetches PR details from Bitbucket API
3. Same review process as webhook-based flow
4. Useful for missed PRs when server was offline

## License

MIT
