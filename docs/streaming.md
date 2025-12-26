# Streaming

Stream extraction results in real-time for responsive applications.

---

## Quick Start

```python
from strutex import DocumentProcessor, StreamingProcessor
from strutex.schemas import INVOICE_US

processor = DocumentProcessor(provider="gemini")
streamer = StreamingProcessor(processor)

# Stream extraction
for chunk in streamer.stream("invoice.pdf", "Extract invoice", INVOICE_US):
    print(chunk.content, end="", flush=True)
```

---

## StreamingProcessor

Wrap any processor for streaming:

```python
from strutex import StreamingProcessor

streamer = StreamingProcessor(processor)

# Sync streaming
for chunk in streamer.stream(file_path, prompt, schema):
    print(chunk.content, end="")

    if chunk.is_complete:
        print("\n--- Complete ---")
```

---

## StreamChunk

Each chunk contains:

| Field         | Type | Description                     |
| ------------- | ---- | ------------------------------- |
| `content`     | str  | New content in this chunk       |
| `is_complete` | bool | Whether this is the final chunk |
| `accumulated` | str  | All content received so far     |
| `metadata`    | dict | Optional metadata               |

```python
for chunk in streamer.stream(...):
    # Current chunk
    print(f"Content: {chunk.content}")

    # Running total
    print(f"So far: {chunk.accumulated}")

    # Check if done
    if chunk.is_complete:
        final_result = json.loads(chunk.accumulated)
```

---

## Async Streaming

```python
import asyncio

async def stream_extract():
    async for chunk in streamer.astream(file_path, prompt, schema):
        print(chunk.content, end="", flush=True)

asyncio.run(stream_extract())
```

---

## Utility Functions

### stream_to_string

Consume entire stream and return final result:

```python
from strutex.providers import stream_to_string

result_str = stream_to_string(streamer.stream(...))
result = json.loads(result_str)
```

### stream_with_callback

Stream with callbacks:

```python
from strutex.providers import stream_with_callback

def on_chunk(chunk):
    print(chunk.content, end="", flush=True)

def on_complete(result):
    print(f"\n\nDone! {len(result)} characters")

result = stream_with_callback(
    streamer.stream(...),
    on_chunk=on_chunk,
    on_complete=on_complete
)
```

---

## Async Helpers

```python
from strutex.providers.streaming import astream_to_string

async def get_result():
    result_str = await astream_to_string(streamer.astream(...))
    return json.loads(result_str)
```

---

## Provider Streaming Support

!!! note "Default Behavior"
By default, StreamingProcessor falls back to non-streaming mode
by calling `process()` and yielding a single complete chunk.

Providers can implement native streaming by adding a `stream()` method:

```python
from strutex.providers import Provider
from strutex.providers.streaming import StreamingMixin, StreamChunk

class MyProvider(Provider, StreamingMixin):
    def stream(self, file_path, prompt, schema, mime_type, **kwargs):
        # Implement native streaming
        for partial in self.api.stream_generate(...):
            yield StreamChunk(
                content=partial,
                is_complete=False,
                accumulated=self._accumulated
            )

        yield StreamChunk(
            content="",
            is_complete=True,
            accumulated=self._accumulated
        )
```

---

## Use Cases

### Progress Indication

```python
import sys

for chunk in streamer.stream(...):
    sys.stdout.write(f"\rReceived {len(chunk.accumulated)} chars...")
    sys.stdout.flush()

print("\nDone!")
```

### Real-time UI Updates

```python
# In a web framework (pseudo-code)
async def stream_endpoint(file_path, prompt, schema):
    async for chunk in streamer.astream(file_path, prompt, schema):
        yield f"data: {json.dumps({'content': chunk.content})}\n\n"
```

### Timeout with Partial Results

```python
import signal

class TimeoutError(Exception):
    pass

def timeout_handler(signum, frame):
    raise TimeoutError()

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm(30)  # 30 second timeout

try:
    result = ""
    for chunk in streamer.stream(...):
        result = chunk.accumulated
    signal.alarm(0)  # Cancel timeout
except TimeoutError:
    print(f"Timed out! Partial result: {result[:100]}...")
```

---

## Best Practices

1. **Use `flush=True`** when printing streaming output
2. **Handle incomplete streams** gracefully
3. **Parse JSON only after `is_complete=True`**
4. **Use async streaming** in async applications
5. **Implement proper error handling** for network issues
