"""
Retry and timeout utilities for providers.

Provides retry logic with exponential backoff for handling transient failures.
"""

import time
import logging
from functools import wraps
from typing import Callable, Optional, Tuple, Type, TypeVar

T = TypeVar("T")

logger = logging.getLogger("strutex.providers.retry")


class RetryConfig:
    """
    Configuration for retry behavior.
    
    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)  
        exponential_base: Base for exponential backoff (default: 2)
        retry_on: Tuple of exception types to retry on
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        retry_on: Optional[Tuple[Type[Exception], ...]] = None
    ):
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.retry_on = retry_on or (Exception,)


# Default config that works well for most LLM APIs
DEFAULT_RETRY_CONFIG = RetryConfig(
    max_retries=3,
    base_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0
)


def with_retry(
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None
):
    """
    Decorator that adds retry logic to a function.
    
    Args:
        config: Retry configuration (uses DEFAULT_RETRY_CONFIG if None)
        on_retry: Optional callback called on each retry (exception, attempt)
        
    Example:
        @with_retry(RetryConfig(max_retries=5))
        def call_api():
            ...
    """
    cfg = config or DEFAULT_RETRY_CONFIG
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            
            for attempt in range(cfg.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except cfg.retry_on as e:
                    last_exception = e
                    
                    if attempt < cfg.max_retries:
                        delay = min(
                            cfg.base_delay * (cfg.exponential_base ** attempt),
                            cfg.max_delay
                        )
                        
                        logger.warning(
                            f"Attempt {attempt + 1} failed: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        
                        if on_retry:
                            on_retry(e, attempt + 1)
                        
                        time.sleep(delay)
                    else:
                        logger.error(
                            f"All {cfg.max_retries + 1} attempts failed. "
                            f"Last error: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator


async def with_retry_async(
    func: Callable[..., T],
    config: Optional[RetryConfig] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
    *args,
    **kwargs
) -> T:
    """
    Async retry wrapper for coroutines.
    
    Args:
        func: Async function to retry
        config: Retry configuration
        on_retry: Optional callback on retry
        *args, **kwargs: Arguments to pass to func
        
    Example:
        result = await with_retry_async(api.call, config, arg1, arg2)
    """
    import asyncio
    
    cfg = config or DEFAULT_RETRY_CONFIG
    last_exception = None
    
    for attempt in range(cfg.max_retries + 1):
        try:
            return await func(*args, **kwargs)
        except cfg.retry_on as e:
            last_exception = e
            
            if attempt < cfg.max_retries:
                delay = min(
                    cfg.base_delay * (cfg.exponential_base ** attempt),
                    cfg.max_delay
                )
                
                logger.warning(
                    f"Async attempt {attempt + 1} failed: {e}. "
                    f"Retrying in {delay:.1f}s..."
                )
                
                if on_retry:
                    on_retry(e, attempt + 1)
                
                await asyncio.sleep(delay)
            else:
                logger.error(
                    f"All {cfg.max_retries + 1} async attempts failed. "
                    f"Last error: {e}"
                )
    
    raise last_exception


class RateLimiter:
    """
    Simple rate limiter for API calls.
    
    Ensures a minimum delay between consecutive calls.
    """
    
    def __init__(self, min_interval: float = 0.0):
        """
        Args:
            min_interval: Minimum seconds between calls
        """
        self.min_interval = min_interval
        self._last_call = 0.0
    
    def wait(self) -> None:
        """Block until it's safe to make another call."""
        if self.min_interval <= 0:
            return
        
        now = time.time()
        elapsed = now - self._last_call
        
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        
        self._last_call = time.time()
    
    async def wait_async(self) -> None:
        """Async version of wait."""
        import asyncio
        
        if self.min_interval <= 0:
            return
        
        now = time.time()
        elapsed = now - self._last_call
        
        if elapsed < self.min_interval:
            await asyncio.sleep(self.min_interval - elapsed)
        
        self._last_call = time.time()
