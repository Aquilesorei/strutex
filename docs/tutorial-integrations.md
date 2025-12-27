# Framework Integrations

Use strutex with LangChain, LlamaIndex, and other AI frameworks.

> [!WARNING] > **Experimental:** These integrations may break with framework updates.
> LangChain, LlamaIndex, and Haystack evolve rapidly. Pin dependency versions.

---

## Overview

Strutex integrates with popular AI/ML frameworks for RAG pipelines:

```
┌─────────────────────────────────────────────────────────────┐
│                     Your RAG Pipeline                        │
├─────────────────────────────────────────────────────────────┤
│  Documents → [Strutex] → Structured JSON → Vector Store     │
│                              ↓                               │
│                     Query → [LLM] → Answer                   │
└─────────────────────────────────────────────────────────────┘
```

---

## Installation

```bash
# LangChain integration
pip install strutex[langchain]

# LlamaIndex integration
pip install strutex[llamaindex]

# Both
pip install strutex[all]
```

---

## LangChain Integration

### StrutexLoader

Use as a LangChain document loader:

```python
from strutex.integrations import StrutexLoader
from strutex.schemas import INVOICE_US

# Create loader
loader = StrutexLoader(
    file_path="invoice.pdf",
    schema=INVOICE_US,
    provider="gemini"
)

# Load documents
documents = loader.load()

# Use in LangChain pipeline
print(documents[0].page_content)  # JSON string
print(documents[0].metadata)       # {"source": "invoice.pdf", ...}
```

### With Vector Store

```python
from strutex.integrations import StrutexLoader
from strutex.schemas import INVOICE_US
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

# Load and extract invoices
loader = StrutexLoader("invoices/jan.pdf", schema=INVOICE_US)
docs = loader.load()

# Create vector store
vectorstore = Chroma.from_documents(docs, OpenAIEmbeddings())

# Query
results = vectorstore.similarity_search("highest total invoice")
```

### StrutexOutputParser

Validate LLM output with strutex schemas:

```python
from strutex.integrations import StrutexOutputParser
from pydantic import BaseModel

class InvoiceData(BaseModel):
    vendor: str
    total: float
    date: str

parser = StrutexOutputParser(
    schema=InvoiceData,
    validators=["schema", "sum"]  # Use strutex validators
)

# Parse LLM response
result = parser.parse(llm_response_text)
print(result.vendor)  # Validated Pydantic model

# Get format instructions for prompts
instructions = parser.get_format_instructions()
```

---

## LlamaIndex Integration

### StrutexReader

Use as a LlamaIndex document reader:

```python
from strutex.integrations import StrutexReader
from strutex.schemas import INVOICE_GENERIC

reader = StrutexReader(
    schema=INVOICE_GENERIC,
    provider="openai"
)

# Load data
documents = reader.load_data("invoice.pdf")

# Build index
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(documents)

# Query
query_engine = index.as_query_engine()
response = query_engine.query("What was the total amount?")
```

### StrutexNodeParser

Keep structured documents as single nodes (prevents chunking):

```python
from strutex.integrations import StrutexReader, StrutexNodeParser

reader = StrutexReader(schema=MySchema)
docs = reader.load_data("complex_doc.pdf")

# Don't chunk structured JSON
parser = StrutexNodeParser()
nodes = parser.get_nodes_from_documents(docs)

# Each document stays as one node
print(len(nodes))  # Same as len(docs)
```

---

## Full RAG Pipeline Example

```python
from strutex.integrations import StrutexLoader
from strutex.schemas import INVOICE_US
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA
from pathlib import Path

# 1. Load all invoices from directory
documents = []
for pdf in Path("invoices/").glob("*.pdf"):
    loader = StrutexLoader(str(pdf), schema=INVOICE_US)
    documents.extend(loader.load())

print(f"Loaded {len(documents)} invoices")

# 2. Create vector store
vectorstore = Chroma.from_documents(
    documents,
    OpenAIEmbeddings()
)

# 3. Build QA chain
qa = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(),
    retriever=vectorstore.as_retriever()
)

# 4. Query your invoices
answer = qa.invoke("Which vendor had the highest total?")
print(answer)

answer = qa.invoke("List all invoices from January")
print(answer)
```

---

## Haystack Integration

Use in Haystack 2.x pipelines:

```python
from strutex.integrations import StrutexConverter
from strutex.schemas import INVOICE_US

converter = StrutexConverter(schema=INVOICE_US)
result = converter.run(sources=["invoice.pdf"])

documents = result["documents"]
```

---

## Unstructured Fallback

Hybrid mode with consistent error handling:

```python
from strutex.integrations import UnstructuredFallbackProcessor, ExtractionError
from strutex.schemas import INVOICE_US

# on_fallback options: "raise" (default), "empty", "partial"
processor = UnstructuredFallbackProcessor(
    schema=INVOICE_US,
    provider="gemini",
    on_fallback="raise"  # Fail loudly for consistent handling
)

try:
    result = processor.process("messy_doc.pdf")
    print(result["vendor_name"])  # Always returns consistent dict shape
except ExtractionError as e:
    print(f"Extraction failed: {e}")
    # Handle failure explicitly
```

**Fallback modes:**

| Mode        | Behavior                                         |
| ----------- | ------------------------------------------------ |
| `"raise"`   | Raise `ExtractionError` on failure (recommended) |
| `"empty"`   | Return empty dict matching schema                |
| `"partial"` | Return empty dict with `_fallback=True` metadata |

---

## Next Steps

| Want to...            | Go to...                                     |
| --------------------- | -------------------------------------------- |
| Handle file uploads   | [DocumentInput](tutorial-document-input.md)  |
| Create custom plugins | [Custom Plugins](tutorial-custom-plugins.md) |
| See built-in schemas  | [Built-in Schemas](schemas.md)               |
