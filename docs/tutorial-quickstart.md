# Quickstart

Extract structured data from your first document in 5 minutes.

## Installation

```bash
pip install strutex
```

## Your First Extraction

```python
from strutex import DocumentProcessor
from strutex.schemas import INVOICE_US

# Create processor
processor = DocumentProcessor(provider="gemini")  # or "openai", "anthropic"

# Extract structured data
result = processor.process(
    file_path="invoice.pdf",
    prompt="Extract invoice details",
    schema=INVOICE_US
)

# Use the result
print(f"Vendor: {result['vendor_name']}")
print(f"Total: ${result['total']}")
print(f"Date: {result['date']}")
```

That's it! You've extracted structured JSON from a document.

---

## What Just Happened?

1. **DocumentProcessor** — The main engine that handles extraction
2. **INVOICE_US** — A built-in schema defining what fields to extract
3. **process()** — Sends the document to an LLM and validates the result

---

## Next Steps

| Want to...              | Go to...                                     |
| ----------------------- | -------------------------------------------- |
| Define your own schema  | [Your First Schema](tutorial-schema.md)      |
| Try different providers | [Switching Providers](tutorial-providers.md) |
| Add data validation     | [Adding Validation](tutorial-validation.md)  |

---

## Troubleshooting

**"API key not found"**

```bash
export GOOGLE_API_KEY="your-key"  # For Gemini
export OPENAI_API_KEY="your-key"  # For OpenAI
```

**"File not found"**

```python
# Use absolute path
result = processor.process("/full/path/to/invoice.pdf", ...)
```
