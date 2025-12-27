# Working with File Uploads

Handle file paths, BytesIO streams, and HTTP uploads with DocumentInput.

---

## The Problem

Your application might receive documents from different sources:

```python
# From file system
file_path = "/path/to/invoice.pdf"

# From HTTP upload (Flask/FastAPI)
uploaded_file = request.files["document"]
file_bytes = uploaded_file.read()

# From cloud storage
blob = bucket.get_blob("invoice.pdf")
content = blob.download_as_bytes()
```

`DocumentProcessor.process()` expects a file path. How do you handle in-memory bytes?

---

## DocumentInput: Unified Interface

`DocumentInput` provides a consistent interface for all input sources:

```python
from strutex import DocumentInput, DocumentProcessor, GeminiProvider
from pathlib import Path
import io

# From file path (string)
doc = DocumentInput("invoice.pdf")

# From Path object
doc = DocumentInput(Path("invoice.pdf"))

# From BytesIO
bytes_data = io.BytesIO(pdf_bytes)
doc = DocumentInput(bytes_data, filename="upload.pdf")
```

---

## Using with DocumentProcessor

Use the `as_file_path()` context manager:

```python
from strutex import DocumentInput, DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

# Works with file path
doc = DocumentInput("invoice.pdf")
with doc.as_file_path() as path:
    result = processor.process(path, "Extract", schema=MySchema)

# Works with BytesIO
doc = DocumentInput(io.BytesIO(pdf_bytes), filename="upload.pdf")
with doc.as_file_path() as path:
    # Temp file is created automatically
    result = processor.process(path, "Extract", schema=MySchema)
# Temp file is cleaned up automatically
```

---

## Flask Example

```python
from flask import Flask, request, jsonify
from strutex import DocumentInput, DocumentProcessor, GeminiProvider
from pydantic import BaseModel

app = Flask(__name__)
processor = DocumentProcessor(provider=GeminiProvider())

class Invoice(BaseModel):
    vendor: str
    total: float
    date: str

@app.route("/extract", methods=["POST"])
def extract_invoice():
    # Get uploaded file
    uploaded = request.files["document"]

    # Create DocumentInput from bytes
    doc = DocumentInput(
        io.BytesIO(uploaded.read()),
        filename=uploaded.filename
    )

    # Process
    with doc.as_file_path() as path:
        result = processor.process(path, "Extract invoice", model=Invoice)

    return jsonify(result.model_dump())
```

---

## FastAPI Example

```python
from fastapi import FastAPI, UploadFile
from strutex import DocumentInput, DocumentProcessor, GeminiProvider
from pydantic import BaseModel
import io

app = FastAPI()
processor = DocumentProcessor(provider=GeminiProvider())

class Invoice(BaseModel):
    vendor: str
    total: float
    date: str

@app.post("/extract")
async def extract_invoice(file: UploadFile):
    # Read file content
    content = await file.read()

    # Create DocumentInput
    doc = DocumentInput(
        io.BytesIO(content),
        filename=file.filename
    )

    # Process
    with doc.as_file_path() as path:
        result = processor.process(path, "Extract invoice", model=Invoice)

    return result.model_dump()
```

---

## DocumentInput Properties

```python
from strutex import DocumentInput

doc = DocumentInput("invoice.pdf")

# Check source type
print(doc.is_file_path)  # True for file paths, False for BytesIO
print(doc.path)          # Original path (or None for BytesIO)
print(doc.filename)      # "invoice.pdf"

# Get raw bytes
content = doc.get_bytes()

# Get MIME type
mime_type = doc.get_mime_type()  # "application/pdf"
```

---

## MIME Type Detection

`DocumentInput` automatically detects MIME types:

```python
doc = DocumentInput(io.BytesIO(data), filename="report.pdf")
print(doc.get_mime_type())  # "application/pdf"

doc = DocumentInput(io.BytesIO(data), filename="scan.png")
print(doc.get_mime_type())  # "image/png"

doc = DocumentInput(io.BytesIO(data), filename="data.xlsx")
print(doc.get_mime_type())  # "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"

# Override MIME type explicitly
doc = DocumentInput(io.BytesIO(data), filename="file.bin", mime_type="application/pdf")
```

---

## Temp File Lifecycle

When using BytesIO, `as_file_path()` creates a temporary file:

```python
doc = DocumentInput(io.BytesIO(pdf_bytes), filename="upload.pdf")

with doc.as_file_path() as path:
    # Temp file exists here
    print(path)  # /tmp/strutex_abc123.pdf

    # Process the file
    result = processor.process(path, "Extract", schema=MySchema)

# Temp file is automatically deleted here
```

**Benefits:**

- No manual cleanup needed
- Works with any processor/extractor
- Preserves file extension for MIME detection

---

## Cloud Storage Examples

### AWS S3

```python
import boto3
import io
from strutex import DocumentInput, DocumentProcessor

s3 = boto3.client("s3")
processor = DocumentProcessor(provider=provider)

# Download from S3
response = s3.get_object(Bucket="my-bucket", Key="invoice.pdf")
content = response["Body"].read()

# Create DocumentInput
doc = DocumentInput(io.BytesIO(content), filename="invoice.pdf")

with doc.as_file_path() as path:
    result = processor.process(path, "Extract", schema=MySchema)
```

### Google Cloud Storage

```python
from google.cloud import storage
import io
from strutex import DocumentInput, DocumentProcessor

client = storage.Client()
bucket = client.bucket("my-bucket")
blob = bucket.blob("invoice.pdf")

# Download
content = blob.download_as_bytes()

# Process
doc = DocumentInput(io.BytesIO(content), filename="invoice.pdf")

with doc.as_file_path() as path:
    result = processor.process(path, "Extract", schema=MySchema)
```

---

## Best Practices

| Practice                                           | Why                               |
| -------------------------------------------------- | --------------------------------- |
| Always use `as_file_path()` context manager        | Ensures temp files are cleaned up |
| Provide `filename` for BytesIO                     | Enables MIME detection            |
| Reuse `DocumentInput` if processing multiple times | Avoids re-reading bytes           |
| Set explicit `mime_type` for unknown extensions    | Prevents detection failures       |

---

## Next Steps

| Want to...            | Go to...                                     |
| --------------------- | -------------------------------------------- |
| Use with LangChain    | [Integrations](tutorial-integrations.md)     |
| Add batch processing  | [Batch & Async](tutorial-batch.md)           |
| Create custom plugins | [Custom Plugins](tutorial-custom-plugins.md) |
