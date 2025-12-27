# Batch & Async Processing

Process multiple documents efficiently.

---

## Batch Processing

Process multiple files in a single call:

```python
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

files = [
    "invoices/jan.pdf",
    "invoices/feb.pdf",
    "invoices/mar.pdf",
]

# Process all files
results = processor.process_batch(
    file_paths=files,
    prompt="Extract invoice details",
    schema=InvoiceSchema
)

for file_path, result in zip(files, results):
    print(f"{file_path}: ${result['total']}")
```

---

## Async Processing

For high-throughput applications, use async:

```python
import asyncio
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

async def extract_invoice(file_path):
    result = await processor.aprocess(
        file_path=file_path,
        prompt="Extract invoice",
        schema=InvoiceSchema
    )
    return result

# Process single file async
result = asyncio.run(extract_invoice("invoice.pdf"))
```

### Concurrent Async Processing

```python
import asyncio
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

async def process_all(files):
    tasks = [
        processor.aprocess(f, "Extract invoice", schema=InvoiceSchema)
        for f in files
    ]
    return await asyncio.gather(*tasks)

files = ["inv1.pdf", "inv2.pdf", "inv3.pdf"]
results = asyncio.run(process_all(files))
```

---

## Batch with Progress

Track progress for large batches:

```python
from tqdm import tqdm
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

files = list(Path("invoices/").glob("*.pdf"))

results = []
for file_path in tqdm(files, desc="Processing"):
    result = processor.process(
        file_path=str(file_path),
        prompt="Extract invoice",
        schema=InvoiceSchema
    )
    results.append(result)
```

---

## Error Handling in Batches

Handle failures gracefully:

```python
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

files = ["good.pdf", "bad.pdf", "also_good.pdf"]
results = []

for file_path in files:
    try:
        result = processor.process(file_path, "Extract", schema=MySchema)
        results.append({"file": file_path, "status": "success", "data": result})
    except Exception as e:
        results.append({"file": file_path, "status": "error", "error": str(e)})

# Check results
success = [r for r in results if r["status"] == "success"]
failed = [r for r in results if r["status"] == "error"]

print(f"Success: {len(success)}, Failed: {len(failed)}")
```

---

## ProcessingContext (Advanced)

Track batch processing state:

```python
from strutex import DocumentProcessor, GeminiProvider
from strutex.context import BatchContext

processor = DocumentProcessor(provider=GeminiProvider())

# Create batch context
context = BatchContext(total_files=len(files))

for file_path in files:
    context.start_file(file_path)

    try:
        result = processor.process(file_path, "Extract", schema=MySchema)
        context.complete_file(file_path, success=True)
    except Exception as e:
        context.complete_file(file_path, success=False, error=str(e))

# Get summary
print(f"Processed: {context.processed_count}/{context.total_files}")
print(f"Success rate: {context.success_rate:.1%}")
print(f"Failed files: {context.failed_files}")
```

---

## Caching with Batches

Combine caching with batch processing:

```python
from strutex import DocumentProcessor, GeminiProvider, MemoryCache

processor = DocumentProcessor(
    provider=GeminiProvider(),
    cache=MemoryCache(max_size=1000)
)

# First run: all API calls
results1 = [processor.process(f, "Extract", schema=MySchema) for f in files]

# Second run: all cached (free!)
results2 = [processor.process(f, "Extract", schema=MySchema) for f in files]
```

---

## Performance Tips

| Tip                               | Impact                     |
| --------------------------------- | -------------------------- |
| Use `MemoryCache`                 | Avoid redundant API calls  |
| Use `aprocess` for I/O bound work | Better throughput          |
| Batch by document type            | Consistent schema handling |
| Add progress tracking             | UX for long jobs           |
| Handle errors per-file            | Don't fail entire batch    |

---

## Next Steps

| Want to...               | Go to...                          |
| ------------------------ | --------------------------------- |
| Integrate with LangChain | [Integrations](integrations.md)   |
| Learn plugin system      | [Plugins](plugins.md)             |
| See full API reference   | [API Reference](api-reference.md) |
