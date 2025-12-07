# Plugin System

Everything in pyapu is pluggable. Use defaults or register your own implementations.

---

## Plugin Types

| Type            | Purpose                 | Built-in Examples                       |
| --------------- | ----------------------- | --------------------------------------- |
| `provider`      | LLM backends            | Gemini, OpenAI                          |
| `security`      | Input/output protection | InputSanitizer, PromptInjectionDetector |
| `extractor`     | Document parsing        | PDF, Image, Excel                       |
| `validator`     | Output validation       | Schema, business rules                  |
| `postprocessor` | Data transformation     | DateNormalizer                          |

---

## Using the Registry

### Register a Plugin

=== "Decorator"

    ```python
    from pyapu.plugins import register, Provider

    @register("provider", name="my_llm")
    class MyProvider(Provider):
        def process(self, file_path, prompt, schema, mime_type, **kwargs):
            return {"result": "data"}
    ```

=== "Manual"

    ```python
    from pyapu.plugins import PluginRegistry

    PluginRegistry.register("provider", "my_llm", MyProvider)
    ```

### Get a Plugin

```python
provider_cls = PluginRegistry.get("provider", "gemini")
```

### List Plugins

```python
all_providers = PluginRegistry.list("provider")
print(all_providers.keys())  # ['gemini', 'geminiprovider', ...]
```

### Discover Installed Plugins

```python
# Auto-discover from pip packages
count = PluginRegistry.discover()
print(f"Found {count} plugins")
```

---

## Creating Custom Plugins

### Custom Provider

```python
from pyapu.plugins import Provider, register

@register("provider")
class OllamaProvider(Provider):
    capabilities = ["local", "vision"]

    def __init__(self, api_key=None, model="llama3"):
        self.model = model

    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        # Call Ollama API
        ...
```

### Custom Validator

```python
from pyapu.plugins import Validator, ValidationResult, register

@register("validator")
class SumValidator(Validator):
    """Verify line items sum to total."""

    def validate(self, data, schema=None):
        items_sum = sum(i.get("amount", 0) for i in data.get("items", []))
        total = data.get("total", 0)

        if abs(items_sum - total) > 0.01:
            return ValidationResult(
                valid=False,
                data=data,
                issues=[f"Sum mismatch: {items_sum} != {total}"]
            )
        return ValidationResult(valid=True, data=data)
```

### Custom Postprocessor

```python
from pyapu.plugins import Postprocessor, register
import re

@register("postprocessor")
class DateNormalizer(Postprocessor):
    """Convert DD.MM.YYYY to YYYY-MM-DD."""

    def process(self, data):
        result = data.copy()
        if "date" in result:
            match = re.match(r'(\d{2})\.(\d{2})\.(\d{4})', result["date"])
            if match:
                d, m, y = match.groups()
                result["date"] = f"{y}-{m}-{d}"
        return result
```

---

## Entry Point Discovery

Publish plugins for pip installation:

```toml title="pyproject.toml"
[project.entry-points."pyapu.providers"]
my_provider = "my_package:MyProvider"

[project.entry-points."pyapu.validators"]
my_validator = "my_package:MyValidator"
```

Users can then discover your plugins automatically:

```python
from pyapu.plugins import PluginRegistry

PluginRegistry.discover()  # Finds my_provider, my_validator
```
