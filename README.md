# pyapu

> **py**thon **A**I **P**DF **U**tilities — Extract structured JSON from documents using LLMs

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

---

## ✨ Features

- 🔌 **Pluggable Architecture** — Everything is extensible with sensible defaults
- 🤖 **Multi-Provider LLM Support** — Gemini, OpenAI, Anthropic, Ollama, and custom endpoints
- 📄 **Universal Document Support** — PDFs, images, Excel, and custom formats
- 🎯 **Schema-Driven Extraction** — Define your output structure, get consistent JSON
- 🔒 **Security First** — Built-in input sanitization and output validation

---

## 🚀 Quick Start

### Installation

```bash
pip install pyapu
```

### Basic Usage

```python
from pyapu import DocumentProcessor, Object, String, Number, Array

# Define your output schema
invoice_schema = Object(
    description="Invoice data",
    properties={
        "invoice_number": String(description="The invoice ID"),
        "total": Number(),
        "items": Array(
            items=Object(
                properties={
                    "description": String(),
                    "amount": Number(),
                }
            )
        )
    }
)

# Process a document
processor = DocumentProcessor(provider="gemini")
result = processor.process(
    file_path="invoice.pdf",
    prompt="Extract the invoice details.",
    schema=invoice_schema
)

print(result["invoice_number"])  # "INV-2024-001"
print(result["total"])           # 1250.00
```

---

## 🔌 Plugin System

**Everything in pyapu is pluggable.** Use defaults or register your own implementations:

```python
from pyapu.plugins import register

@register("provider")
class MyCustomProvider(Provider):
    def process(self, file, prompt, schema):
        # Your custom LLM logic
        ...

@register("postprocessor")
class CurrencyNormalizer(Postprocessor):
    def process(self, data: dict) -> dict:
        # Normalize currency values
        ...
```

### Plugin Types

| Type            | Purpose                 | Examples                          |
| --------------- | ----------------------- | --------------------------------- |
| `provider`      | LLM backends            | Gemini, OpenAI, Claude, Ollama    |
| `security`      | Input/output protection | Injection detection, sanitization |
| `extractor`     | Document parsing        | PDF, Image OCR, Excel             |
| `validator`     | Output validation       | Schema, sum checks, date formats  |
| `postprocessor` | Data transformation     | Date/number normalization         |
| `verifier`      | Quality assurance       | LLM self-correction               |

---

## 📦 Supported Formats

| Format | Extensions              | Method                              |
| ------ | ----------------------- | ----------------------------------- |
| PDF    | `.pdf`                  | Text extraction with fallback chain |
| Images | `.png`, `.jpg`, `.tiff` | Direct vision or OCR                |
| Excel  | `.xlsx`, `.xls`         | Converted to structured text        |
| Text   | `.txt`, `.csv`          | Direct input                        |

---

## 🛣️ Roadmap

See [ROADMAP.md](ROADMAP.md) for the full development plan.

**Current priorities:**

- [x] Plugin registry system (v0.2.0) ✅
- [x] Security plugin layer ✅
- [x] Pydantic model support ✅
- [ ] Additional providers (OpenAI, Anthropic, Ollama)

---

## 📚 Documentation

```bash
# Serve locally (live reload)
poetry run mkdocs serve

# Build static site
poetry run mkdocs build

# Deploy to GitHub Pages
poetry run mkdocs gh-deploy
```

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** — see [LICENSE](LICENSE) for details.

For commercial or proprietary use, please [contact me](mailto:your-email@example.com) for a separate license.

---

## 🤝 Contributing

Contributions are welcome! Priority areas:

1. **New plugins** — Providers, extractors, validators
2. **Documentation** — Examples and tutorials
3. **Testing** — Expand test coverage
