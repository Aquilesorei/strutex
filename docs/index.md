# Strutex

**Python AI PDF Utilities** — Extract structured JSON from documents using LLMs.

---

## Quick Example

```python
from strutex import DocumentProcessor, GeminiProvider
from pydantic import BaseModel

class Invoice(BaseModel):
    invoice_number: str
    vendor: str
    total: float

processor = DocumentProcessor(provider=GeminiProvider())
result = processor.process("invoice.pdf", "Extract invoice data", model=Invoice)

print(result.invoice_number)  # Validated Pydantic model
```

---

## Documentation Map

### 📚 Tutorial (Start Here)

Progressive learning path from basics to advanced:

| #   | Page                                         | Description                                    |
| --- | -------------------------------------------- | ---------------------------------------------- |
| 1   | [Quickstart](tutorial-quickstart.md)         | First extraction in 5 minutes                  |
| 2   | [Your First Schema](tutorial-schema.md)      | Define custom schemas (Pydantic & native)      |
| 3   | [Switching Providers](tutorial-providers.md) | Configure GeminiProvider, OpenAIProvider, etc. |
| 4   | [Adding Validation](tutorial-validation.md)  | Validators and verification loop               |
| 5   | [Caching](tutorial-caching.md)               | MemoryCache, SQLiteCache, FileCache            |
| 6   | [Processing Hooks](tutorial-hooks.md)        | Pre/post processing hooks                      |
| 7   | [Input Sanitization](tutorial-security.md)   | Input cleaning, PII redaction                  |
| 8   | [Batch & Async](tutorial-batch.md)           | process_batch, aprocess                        |
| 9   | [Streaming](tutorial-streaming.md)           | Real-time extraction feedback                  |
| 10  | [Error Handling](tutorial-error-handling.md) | Errors, retries, debugging                     |
| 11  | [File Uploads](tutorial-document-input.md)   | BytesIO, Flask, FastAPI                        |
| 12  | [Integrations](tutorial-integrations.md)     | LangChain, LlamaIndex (Experimental)           |
| 13  | [Custom Plugins](tutorial-custom-plugins.md) | Create Provider, Extractor, SecurityPlugin     |
| 14  | [Use Cases](tutorial-use-cases.md)           | Invoice, Receipt, Resume examples              |
| 15  | [Prompt Engineering](tutorial-prompts.md)    | StructuredPrompt builder                       |

---

### 📖 User Guide

Reference documentation for core features:

| Section     | Pages                                                                                              |
| ----------- | -------------------------------------------------------------------------------------------------- |
| **Schemas** | [Schema Types](schema-types.md) · [Built-in Schemas](schemas.md) · [Pydantic Support](pydantic.md) |
| **Prompts** | [Prompt Builder](prompt-builder.md) · [Verification](verification.md)                              |

---

### ⚡ Providers

LLM provider configuration and optimization:

| Page                                  | Description                    |
| ------------------------------------- | ------------------------------ |
| [Overview](providers.md)              | All supported providers        |
| [Provider Chains](provider-chains.md) | Fallback and cost optimization |
| [Caching Reference](cache.md)         | Detailed cache API             |

---

### 🔌 Integrations

Use with popular AI frameworks:

| Page                            | Description                                   |
| ------------------------------- | --------------------------------------------- |
| [Integrations](integrations.md) | LangChain, LlamaIndex, Haystack, Unstructured |

---

### 🔧 Advanced

For power users and contributors:

| Page                             | Description                     |
| -------------------------------- | ------------------------------- |
| [Plugin System](plugins.md)      | Full plugin API reference       |
| [Hooks Reference](hooks.md)      | Hook specifications             |
| [Processing Context](context.md) | BatchContext, ProcessingContext |
| [Streaming](streaming.md)        | Streaming API reference         |
| [CLI Commands](cli.md)           | Command-line interface          |

---

### 🏗️ Architecture

Internal design and extension points:

| Page                              | Description                  |
| --------------------------------- | ---------------------------- |
| [Extractors](extractors.md)       | PDF, Excel, Image extractors |
| [Validators](validators.md)       | Schema, Sum, Date validators |
| [Input Sanitization](security.md) | Sanitization API             |

---

### 📋 Reference

| Page                              | Description            |
| --------------------------------- | ---------------------- |
| [API Reference](api-reference.md) | Full API documentation |
| [Changelog](changelog.md)         | Version history        |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     DocumentProcessor                        │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐    │
│  │ Security │→ │ Extractor│→ │ Provider │→ │Validator │    │
│  │  Chain   │  │  Plugin  │  │  Plugin  │  │  Plugin  │    │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘    │
│         ↓            ↓            ↓            ↓            │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                   Plugin Registry                       │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Features

| Feature                    | Description                                       |
| -------------------------- | ------------------------------------------------- |
| **15 Tutorials**           | Progressive learning path                         |
| **6 Providers**            | Gemini, OpenAI, Anthropic, Ollama, Groq, Langdock |
| **Plugin System**          | Extend with custom providers, validators          |
| **Pydantic Support**       | Type-safe extractions                             |
| **Caching**                | Reduce API costs                                  |
| **Framework Integrations** | LangChain, LlamaIndex, Haystack                   |
| **Security Layer**         | Injection detection, PII redaction                |
| **CLI Tools**              | `strutex run`, `strutex prompt build`             |

---

## Installation

```bash
pip install strutex

# With integrations
pip install strutex[langchain]
pip install strutex[all]
```

[→ Getting Started](getting-started.md)
