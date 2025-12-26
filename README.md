# Bitbucket PR Code Review Automation

Automated code review system for Bitbucket Cloud pull requests using Claude Code CLI.

## Features

- Webhook-based PR detection for `feature/*` and `fix/*` branches
- Automatic repository cloning and diff extraction
- AI-powered code review using Claude Code CLI
- Flutter/Dart focused review criteria (Clean Architecture, BLoC/Cubit patterns)
- Automatic PR comment posting with review results

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
├── main.py                 # Entry point
├── src/
│   ├── server.py           # FastAPI webhook handler
│   ├── pr_processor.py     # PR review orchestrator
│   ├── bitbucket_client.py # Bitbucket API client
│   ├── git_operations.py   # Git operations
│   ├── claude_reviewer.py  # Claude CLI integration
│   └── utils/
│       ├── retry.py        # Retry decorator
│       └── notifications.py
├── config/
│   ├── logging_config.py
│   └── review_prompts.py
└── requirements.txt
```

## How It Works

1. PR is created from `feature/*` or `fix/*` to `development`
2. Bitbucket sends webhook to your server
3. Server clones the repository to temp directory
4. Extracts diff for Dart files
5. Sends diff to Claude Code CLI for review
6. Posts review comment back to PR
7. Cleans up temp directory

## License

MIT
