"""
Streaming support for document extraction.

Provides async generators for real-time streaming of extraction results.
"""

import json
import logging
from typing import Any, AsyncIterator, Dict, Iterator, Optional, Callable
from dataclasses import dataclass

from ..types import Schema
from ..adapters import SchemaAdapter

logger = logging.getLogger("strutex.providers.streaming")


@dataclass
class StreamChunk:
    """A chunk of streaming response."""
    content: str
    is_complete: bool = False
    accumulated: str = ""
    metadata: Optional[Dict[str, Any]] = None


class StreamingMixin:
    """
    Mixin that adds streaming support to providers.
    
    Providers can inherit from this to add streaming capabilities.
    
    Example:
        class MyProvider(Provider, StreamingMixin):
            def stream(self, file_path, prompt, schema, mime_type):
                for chunk in self._stream_api_call(...):
                    yield StreamChunk(content=chunk)
    """
    
    def stream(
        self,
        file_path: str,
        prompt: str,
        schema: Schema,
        mime_type: str,
        **kwargs
    ) -> Iterator[StreamChunk]:
        """
        Stream extraction results.
        
        Default implementation calls process() and yields single chunk.
        Override for true streaming support.
        
        Yields:
            StreamChunk with partial/complete content
        """
        # Default: call non-streaming and yield single result
        result = self.process(file_path, prompt, schema, mime_type, **kwargs)  # type: ignore
        content = json.dumps(result) if isinstance(result, dict) else str(result)
        
        yield StreamChunk(
            content=content,
            is_complete=True,
            accumulated=content
        )
    
    async def astream(
        self,
        file_path: str,
        prompt: str,
        schema: Schema,
        mime_type: str,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Async stream extraction results.
        
        Default implementation calls aprocess() and yields single chunk.
        
        Yields:
            StreamChunk with partial/complete content
        """
        result = await self.aprocess(file_path, prompt, schema, mime_type, **kwargs)  # type: ignore
        content = json.dumps(result) if isinstance(result, dict) else str(result)
        
        yield StreamChunk(
            content=content,
            is_complete=True,
            accumulated=content
        )


class StreamingProcessor:
    """
    Wrapper that adds streaming to DocumentProcessor.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.providers.streaming import StreamingProcessor
        >>> 
        >>> processor = DocumentProcessor(provider="gemini")
        >>> streamer = StreamingProcessor(processor)
        >>> 
        >>> # Sync streaming
        >>> for chunk in streamer.stream("invoice.pdf", "Extract", INVOICE_US):
        ...     print(chunk.content, end="", flush=True)
        >>> 
        >>> # Async streaming
        >>> async for chunk in streamer.astream("invoice.pdf", "Extract", INVOICE_US):
        ...     print(chunk.content, end="", flush=True)
    """
    
    def __init__(self, processor):
        """
        Args:
            processor: DocumentProcessor instance
        """
        self.processor = processor
    
    def stream(
        self,
        file_path: str,
        prompt: str,
        schema: Any,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> Iterator[StreamChunk]:
        """
        Stream extraction with automatic MIME detection.
        
        Args:
            file_path: Path to document
            prompt: Extraction prompt  
            schema: Output schema or Pydantic model
            mime_type: Optional MIME type (auto-detected if not provided)
            
        Yields:
            StreamChunk objects with partial content
        """
        from ..documents import get_mime_type
        
        if mime_type is None:
            mime_type = get_mime_type(file_path)
        
        provider = self._get_provider()
        
        if hasattr(provider, 'stream'):
            # Provider supports streaming
            yield from provider.stream(file_path, prompt, schema, mime_type, **kwargs)
        else:
            # Fall back to non-streaming
            result = self.processor.process(
                file_path=file_path,
                prompt=prompt,
                schema=schema,
                **kwargs
            )
            content = json.dumps(result, indent=2)
            yield StreamChunk(content=content, is_complete=True, accumulated=content)
    
    async def astream(
        self,
        file_path: str,
        prompt: str,
        schema: Any,
        mime_type: Optional[str] = None,
        **kwargs
    ) -> AsyncIterator[StreamChunk]:
        """
        Async stream extraction.
        
        Yields:
            StreamChunk objects with partial content
        """
        from ..documents import get_mime_type
        
        if mime_type is None:
            mime_type = get_mime_type(file_path)
        
        provider = self._get_provider()
        
        if hasattr(provider, 'astream'):
            async for chunk in provider.astream(file_path, prompt, schema, mime_type, **kwargs):
                yield chunk
        else:
            # Fall back to non-streaming
            if hasattr(self.processor, 'aprocess'):
                result = await self.processor.aprocess(
                    file_path=file_path,
                    prompt=prompt,
                    schema=schema,
                    **kwargs
                )
            else:
                result = self.processor.process(
                    file_path=file_path,
                    prompt=prompt,
                    schema=schema,
                    **kwargs
                )
            
            content = json.dumps(result, indent=2)
            yield StreamChunk(content=content, is_complete=True, accumulated=content)
    
    def _get_provider(self):
        """Get the provider from processor."""
        if hasattr(self.processor, '_provider'):
            return self.processor._provider
        elif hasattr(self.processor, 'provider'):
            return self.processor.provider
        return None


def stream_to_string(stream: Iterator[StreamChunk]) -> str:
    """
    Consume a stream and return the final accumulated string.
    
    Example:
        >>> result = stream_to_string(streamer.stream(...))
        >>> data = json.loads(result)
    """
    last_chunk = None
    for chunk in stream:
        last_chunk = chunk
    
    return last_chunk.accumulated if last_chunk else ""


async def astream_to_string(stream: AsyncIterator[StreamChunk]) -> str:
    """Async version of stream_to_string."""
    last_chunk = None
    async for chunk in stream:
        last_chunk = chunk
    
    return last_chunk.accumulated if last_chunk else ""


def stream_with_callback(
    stream: Iterator[StreamChunk],
    on_chunk: Callable[[StreamChunk], Any],
    on_complete: Optional[Callable[[str], Any]] = None
) -> str:
    """
    Stream with callbacks for each chunk.
    
    Example:
        >>> def print_chunk(chunk):
        ...     print(chunk.content, end="", flush=True)
        >>> 
        >>> result = stream_with_callback(
        ...     streamer.stream(...),
        ...     on_chunk=print_chunk,
        ...     on_complete=lambda s: print(f"\\nDone: {len(s)} chars")
        ... )
    """
    accumulated = ""
    
    for chunk in stream:
        on_chunk(chunk)
        accumulated = chunk.accumulated
    
    if on_complete:
        on_complete(accumulated)
    
    return accumulated
