# Switching Providers

Learn to configure and use different LLM providers for extraction.

---

## Creating Provider Instances

The recommended way to use providers is to create instances directly:

```python
from strutex import DocumentProcessor
from strutex import GeminiProvider, OpenAIProvider, AnthropicProvider

# Create a provider instance
provider = GeminiProvider(
    api_key="your-api-key",  # Or uses GOOGLE_API_KEY env var
    model="gemini-2.0-flash"
)

# Use it with the processor
processor = DocumentProcessor(provider=provider)

result = processor.process("invoice.pdf", "Extract data", schema=MySchema)
```

---

## All Available Providers

### GeminiProvider (Google)

```python
from strutex import GeminiProvider

provider = GeminiProvider(
    api_key="your-key",          # Or GOOGLE_API_KEY env var
    model="gemini-2.0-flash",    # Default model
)

# Access provider info
print(provider.name)    # "gemini"
print(provider.model)   # "gemini-2.0-flash"
```

### OpenAIProvider

```python
from strutex import OpenAIProvider

provider = OpenAIProvider(
    api_key="sk-...",            # Or OPENAI_API_KEY env var
    model="gpt-4o",              # Default: gpt-4o-mini
)
```

### AnthropicProvider (Claude)

```python
from strutex import AnthropicProvider

provider = AnthropicProvider(
    api_key="your-key",                      # Or ANTHROPIC_API_KEY env var
    model="claude-sonnet-4-20250514",    # Default
)
```

### OllamaProvider (Local)

```python
from strutex import OllamaProvider

provider = OllamaProvider(
    model="llama3",
    base_url="http://localhost:11434"  # Default Ollama URL
)
```

### GroqProvider (Fast)

```python
from strutex import GroqProvider

provider = GroqProvider(
    api_key="your-key",          # Or GROQ_API_KEY env var
    model="llama-3.3-70b-versatile"
)
```

### LangdockProvider (Enterprise)

```python
from strutex import LangdockProvider

provider = LangdockProvider(
    api_key="your-key",
    model="gpt-4o",
    region="eu"  # EU or US region
)
```

---

## Choosing a Provider

| Need                   | Provider                               | Why                 |
| ---------------------- | -------------------------------------- | ------------------- |
| **Privacy/Air-gapped** | `OllamaProvider`                       | Runs locally        |
| **Speed**              | `GroqProvider`                         | Fastest inference   |
| **Quality**            | `OpenAIProvider` / `AnthropicProvider` | Best accuracy       |
| **Cost efficiency**    | `GeminiProvider`                       | Free tier, low cost |
| **Long documents**     | `AnthropicProvider`                    | 200K context        |
| **Enterprise/EU**      | `LangdockProvider`                     | GDPR compliant      |

---

## Provider Chains

Fall back gracefully between providers:

```python
from strutex import DocumentProcessor, ProviderChain, RetryConfig
from strutex import GeminiProvider, OpenAIProvider, OllamaProvider

# Create providers
gemini = GeminiProvider(model="gemini-2.0-flash")
openai = OpenAIProvider(model="gpt-4o")
ollama = OllamaProvider(model="llama3")

# Chain them: try in order, fall back on failure
chain = ProviderChain(
    providers=[ollama, gemini, openai],  # Try local first
    retry_config=RetryConfig(max_retries=2)
)

processor = DocumentProcessor(provider=chain)
```

### Pre-built Chains

```python
from strutex import local_first_chain, cost_optimized_chain

# Try local Ollama first, fall back to cloud
chain = local_first_chain(
    local_model="llama3",
    cloud_provider="gemini"
)

# Try cheapest providers first
chain = cost_optimized_chain(["groq", "gemini", "openai"])

processor = DocumentProcessor(provider=chain)
```

---

## HybridProvider (Auto-Select)

Automatically choose provider based on document:

```python
from strutex import HybridProvider, HybridStrategy
from strutex import GeminiProvider, AnthropicProvider

hybrid = HybridProvider(
    providers={
        "default": GeminiProvider(),
        "long_document": AnthropicProvider(),  # For docs > 50 pages
    },
    strategy=HybridStrategy.DOCUMENT_SIZE
)

processor = DocumentProcessor(provider=hybrid)
```

---

## Accessing Provider Name

After creating a processor, you can access the provider name:

```python
processor = DocumentProcessor(provider=GeminiProvider())
print(processor.provider_name)  # "gemini"
```

---

## Environment Variables

Each provider checks for its API key in environment variables:

```bash
# Set in your shell or .env file
export GOOGLE_API_KEY="your-gemini-key"
export OPENAI_API_KEY="your-openai-key"
export ANTHROPIC_API_KEY="your-anthropic-key"
export GROQ_API_KEY="your-groq-key"
```

```python
# Then create provider without explicit key
provider = GeminiProvider()  # Uses GOOGLE_API_KEY
```

---

## Next Steps

| Want to...           | Go to...                                    |
| -------------------- | ------------------------------------------- |
| Add validation rules | [Adding Validation](tutorial-validation.md) |
| Configure caching    | [Caching](tutorial-caching.md)              |
| Add hooks            | [Processing Hooks](tutorial-hooks.md)       |
