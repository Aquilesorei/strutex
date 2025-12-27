# Processing Hooks

Customize extraction behavior with pre/post processing hooks.

---

## What Are Hooks?

Hooks let you run custom code at specific points in the extraction pipeline:

```
Document → [Pre-Process Hook] → LLM Extraction → [Post-Process Hook] → Result
                                      ↓
                              [Error Hook] (on failure)
```

---

## Adding Hooks via Constructor

```python
from strutex import DocumentProcessor, GeminiProvider

def log_before(file_path, prompt, schema, mime_type, context):
    print(f"Processing: {file_path}")
    return None  # Return None to keep original values

def add_metadata(result, context):
    result["processed_at"] = "2024-01-01"
    result["processor_version"] = "1.0"
    return result

def handle_error(error, file_path, context):
    print(f"Error processing {file_path}: {error}")
    return None  # Return None to re-raise, or return fallback dict

processor = DocumentProcessor(
    provider=GeminiProvider(),
    on_pre_process=log_before,
    on_post_process=add_metadata,
    on_error=handle_error
)
```

---

## Adding Hooks via Decorators

```python
from strutex import DocumentProcessor, GeminiProvider
from datetime import datetime

processor = DocumentProcessor(provider=GeminiProvider())

@processor.on_pre_process
def log_start(file_path, prompt, schema, mime_type, context):
    context["start_time"] = datetime.now()
    print(f"Starting extraction: {file_path}")

@processor.on_post_process
def add_timing(result, context):
    elapsed = datetime.now() - context["start_time"]
    result["extraction_time_seconds"] = elapsed.total_seconds()
    return result

@processor.on_error
def fallback_handler(error, file_path, context):
    # Return empty dict as fallback instead of raising
    return {"error": str(error), "file": file_path}
```

---

## Pre-Process Hook

Runs **before** LLM extraction. Can modify inputs.

```python
def pre_process(file_path, prompt, schema, mime_type, context):
    """
    Args:
        file_path: Path to document
        prompt: Extraction prompt
        schema: Schema being used
        mime_type: Detected MIME type
        context: Mutable dict for sharing data between hooks

    Returns:
        None - keep original values
        dict - override values, e.g. {"prompt": "Modified prompt"}
    """
    # Example: Add context to prompt based on file type
    if mime_type == "application/pdf":
        return {"prompt": prompt + "\nThis is a PDF document."}
    return None
```

---

## Post-Process Hook

Runs **after** successful extraction. Can modify result.

```python
def post_process(result, context):
    """
    Args:
        result: Extracted dict from LLM
        context: Context dict from pre-process

    Returns:
        Modified result dict (or original if unchanged)
    """
    # Example: Normalize currency values
    if "total" in result:
        result["total"] = round(result["total"], 2)

    # Example: Add audit trail
    result["_source_file"] = context.get("file_path")

    return result
```

---

## Error Hook

Runs when extraction fails. Can provide fallback.

```python
def error_handler(error, file_path, context):
    """
    Args:
        error: The exception that occurred
        file_path: File being processed
        context: Context dict

    Returns:
        None - re-raise the original error
        dict - use as fallback result
    """
    # Log to external service
    logging.error(f"Extraction failed: {error}")

    # Option 1: Return fallback
    return {"extraction_failed": True, "error": str(error)}

    # Option 2: Re-raise
    return None
```

---

## Multiple Hooks

You can register multiple hooks of the same type:

```python
@processor.on_post_process
def add_timestamp(result, context):
    result["timestamp"] = datetime.now().isoformat()
    return result

@processor.on_post_process
def validate_totals(result, context):
    if result.get("total", 0) < 0:
        result["_warning"] = "Negative total detected"
    return result

# Both hooks run in order
```

---

## Real-World Examples

### Logging & Monitoring

```python
import logging
from datetime import datetime

@processor.on_pre_process
def log_request(file_path, prompt, schema, mime_type, context):
    context["request_id"] = str(uuid.uuid4())
    logging.info(f"[{context['request_id']}] Starting: {file_path}")

@processor.on_post_process
def log_response(result, context):
    logging.info(f"[{context['request_id']}] Complete: {len(result)} fields")
    return result
```

### Data Normalization

```python
@processor.on_post_process
def normalize_invoice(result, context):
    # Standardize date format
    if "date" in result:
        from dateutil import parser
        result["date"] = parser.parse(result["date"]).strftime("%Y-%m-%d")

    # Ensure currency format
    for field in ["total", "subtotal", "tax"]:
        if field in result:
            result[field] = round(float(result[field]), 2)

    return result
```

---

## Next Steps

| Want to...          | Go to...                              |
| ------------------- | ------------------------------------- |
| Add security checks | [Security](tutorial-security.md)      |
| Process in batches  | [Batch Processing](tutorial-batch.md) |
| Use with LangChain  | [Integrations](integrations.md)       |
