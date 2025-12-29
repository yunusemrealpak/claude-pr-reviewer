# Bitbucket PR Code Review Automation

Automated code review system for Bitbucket Cloud pull requests using Claude Code CLI.

## Features

- Webhook-based PR detection for `feature/*` and `fix/*` branches
- Manual PR review trigger via CLI tool (for missed PRs when server is offline)
- Automatic repository cloning and diff extraction
- AI-powered code review using Claude Code CLI
- Flutter/Dart focused review criteria (Clean Architecture, BLoC/Cubit patterns)
- Automatic PR comment posting with review results
- Multi-language support (Turkish & English)

## Architecture

```
Bitbucket PR → Webhook → FastAPI Server → Clone Repo → Claude Code CLI → PR Comment
```

## Requirements

- Python 3.10+
- Claude Code CLI (with active subscription)
- ngrok or cloudflared (for webhook tunneling)
- Bitbucket Cloud account with API token

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
```

### 5. Authenticate Claude Code CLI

```bash
claude auth login
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
   - **Triggers**: `Pull Request: Created`

## Bitbucket API Token Setup

1. Go to **Personal Settings** → **API tokens**
2. Create token with scopes:
   - `read:repository:bitbucket`
   - `read:pullrequest:bitbucket`
   - `write:pullrequest:bitbucket`

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

1. PR is created from `feature/*` or `fix/*` to `development`
2. Bitbucket sends webhook to your server
3. Server clones the repository to temp directory
4. Extracts diff for Dart files
5. Sends diff to Claude Code CLI for review
6. Posts review comment back to PR
7. Cleans up temp directory

### Manual Trigger

1. Run `python -m src.trigger_review` with PR information
2. Tool fetches PR details from Bitbucket API
3. Same review process as webhook-based flow
4. Useful for missed PRs when server was offline

## License

MIT
