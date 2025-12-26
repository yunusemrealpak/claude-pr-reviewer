"""Retry mechanism with exponential backoff for failed operations."""

import time
import logging
from functools import wraps
from typing import Type, Tuple, Callable, Any
import requests

logger = logging.getLogger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    exceptions: Tuple[Type[Exception], ...] = (requests.RequestException,)
) -> Callable:
    """
    Decorator that retries failed operations with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries in seconds
        exceptions: Tuple of exception types to catch and retry

    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries - 1:
                        logger.error(
                            f"All {max_retries} attempts failed for {func.__name__}"
                        )
                        raise

                    delay = base_delay * (2 ** attempt)
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed, "
                        f"retrying in {delay}s: {e}"
                    )
                    time.sleep(delay)

            raise last_exception  # type: ignore

        return wrapper
    return decorator
