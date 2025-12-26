"""Main entry point for PR Code Review Automation server."""

import os
import uvicorn
from dotenv import load_dotenv

from config.logging_config import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
log_level = os.getenv("LOG_LEVEL", "INFO")
setup_logging(log_level)


def main() -> None:
    """Start the FastAPI server."""
    host = os.getenv("SERVER_HOST", "0.0.0.0")
    port = int(os.getenv("SERVER_PORT", "8000"))

    uvicorn.run(
        "src.server:app",
        host=host,
        port=port,
        reload=False
    )


if __name__ == "__main__":
    main()
