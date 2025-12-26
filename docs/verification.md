# Verification & Self-Correction

Strutex v0.8.0 introduces **Verification**, a powerful mechanism to improve extraction accuracy by using the LLM to audit and correct its own work.

## Overview

Extraction errors can happen, especially with complex documents. The Verification feature runs a **two-step workflow**:

1.  **Extraction**: The document is processed normally to generate structured JSON.
2.  **Audit**: The result from step 1 is fed back to the LLM (or a different model) along with the original document. The model acts as a "strict auditor" to check for discrepancies and fix them.

This "Reflexion" pattern significantly reduces hallucinations and missing fields.

---

## Usage

### Automatic Verification

The simplest way to use verification is to pass `verify=True` to the `process` (or `aprocess`) method.

```python
from strutex import DocumentProcessor
from strutex.schemas import INVOICE_US

processor = DocumentProcessor()

result = processor.process(
    file_path="invoice.pdf",
    prompt="Extract invoice data",
    schema=INVOICE_US,
    verify=True  # 👈 Enables self-correction loop
)
```

### Manual Verification

You can also run verification on a result you already have (e.g., from a previous run or a different system).

```python
previous_result = {
    "invoice_number": "INV-001",
    "total": 500.00  # Suspicious value
}

verified_result = processor.verify(
    file_path="invoice.pdf",
    result=previous_result,
    schema=INVOICE_US
)
```

### Async Support

Verification is fully supported in async workflows:

```python
result = await processor.aprocess(
    ...,
    verify=True
)

# Or manually:
result = await processor.averify(...)
```

---

## Configuration

### Custom Verification Prompt

By default, Strutex uses a generic "strict auditor" system prompt. You can customize this to look for specific errors.

```python
result = processor.process(
    ...,
    verify=True,
    verify_prompt="Check strictly that the 'total' matches the sum of line items."
)
```

---

## Performance & Cost

Enabling verification **doubles** the number of LLM calls (1 extraction + 1 verification). This increases:

- **Latency**: Expect roughly 2x processing time.
- **Cost**: Expect roughly 2x token usage.

!!! note "Usage Tracking"
With `verify=True`, usage statistics (tokens/cost) in the returned result only reflect the **verification pass**. If you need total cost tracking, ensure you are logging usage from your quota manager or provider dashboard.

## Best Practices

- Use `verify=True` for critical data fields where accuracy is paramount (e.g. financial totals).
- For high-volume low-value documents, you might skip verification to save costs.
- Consider using a faster/cheaper model for extraction and a stronger model for verification (currently requires manual 2-step calls).
