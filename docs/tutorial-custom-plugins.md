# Creating Custom Plugins

Extend strutex with your own providers, extractors, and security plugins.

---

## Plugin System Overview

Strutex uses an inheritance-based plugin system. To create a custom plugin:

1. Inherit from the appropriate base class
2. Implement required methods
3. Your plugin is auto-registered!

```
┌────────────────────────────────────────────────────┐
│                 Plugin Types                        │
├────────────────────────────────────────────────────┤
│ Provider      → Custom LLM backends                │
│ Extractor     → Custom file format handlers        │
│ SecurityPlugin → Custom security validation        │
└────────────────────────────────────────────────────┘
```

---

## Creating a Custom Provider

Create your own LLM provider by inheriting from `Provider`:

```python
from strutex.plugins.base import Provider
from typing import Any, Optional

class MyCustomProvider(Provider, name="my_provider"):
    """
    Custom LLM provider for internal API.

    Inheriting from Provider auto-registers the plugin!
    """

    # Plugin metadata (optional)
    priority = 50      # Lower = higher priority
    cost = 0.001       # Cost per request for chain sorting
    version = "1.0.0"

    def __init__(self, api_key: Optional[str] = None, model: str = "default"):
        self.api_key = api_key
        self.model = model

    def process(
        self,
        file_path: str,
        prompt: str,
        schema: Any,
        mime_type: str,
        **kwargs
    ) -> dict:
        """
        Main extraction method. Required.

        Args:
            file_path: Path to document
            prompt: Extraction prompt
            schema: Target schema
            mime_type: File MIME type
            **kwargs: Additional options

        Returns:
            Extracted data as dict
        """
        # 1. Read the file
        with open(file_path, "rb") as f:
            content = f.read()

        # 2. Call your LLM API
        response = self._call_api(content, prompt, schema)

        # 3. Parse and return
        return response

    def _call_api(self, content: bytes, prompt: str, schema: Any) -> dict:
        """Your API implementation."""
        import requests

        response = requests.post(
            "https://your-api.com/extract",
            json={
                "content": content.decode("utf-8"),
                "prompt": prompt,
                "schema": schema.to_dict() if hasattr(schema, "to_dict") else schema
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        return response.json()

    def health_check(self) -> bool:
        """Optional: Check if provider is available."""
        try:
            # Ping your API
            return True
        except Exception:
            return False
```

### Using Your Custom Provider

```python
from strutex import DocumentProcessor
from my_providers import MyCustomProvider

# Create instance
provider = MyCustomProvider(api_key="secret", model="v2")

# Use with processor
processor = DocumentProcessor(provider=provider)
result = processor.process("doc.pdf", "Extract", schema=MySchema)

# Or use by name (auto-registered!)
processor = DocumentProcessor(provider="my_provider")
```

---

## Creating a Custom Extractor

Handle custom file formats by inheriting from `Extractor`:

```python
from strutex.plugins.base import Extractor
from typing import Any

class XMLExtractor(Extractor, name="xml"):
    """Extract data from XML files."""

    # Supported MIME types
    supported_types = ["application/xml", "text/xml"]

    def extract(self, file_path: str, **kwargs) -> str:
        """
        Extract text content from file.

        Args:
            file_path: Path to file
            **kwargs: Additional options

        Returns:
            Text content for LLM
        """
        import xml.etree.ElementTree as ET

        tree = ET.parse(file_path)
        root = tree.getroot()

        # Convert XML to readable text
        return self._xml_to_text(root)

    def _xml_to_text(self, element, indent=0) -> str:
        """Recursively convert XML to text."""
        lines = []
        prefix = "  " * indent

        if element.text and element.text.strip():
            lines.append(f"{prefix}{element.tag}: {element.text.strip()}")
        else:
            lines.append(f"{prefix}{element.tag}:")

        for child in element:
            lines.append(self._xml_to_text(child, indent + 1))

        return "\n".join(lines)

    def supports(self, mime_type: str) -> bool:
        """Check if this extractor handles the MIME type."""
        return mime_type in self.supported_types
```

### Registering Your Extractor

```python
from strutex.plugins.registry import PluginRegistry
from my_extractors import XMLExtractor

# Auto-registered via inheritance, but you can also manually register
PluginRegistry.register("extractor", XMLExtractor, name="xml")

# Now XML files are automatically handled
processor = DocumentProcessor(provider=provider)
result = processor.process("data.xml", "Extract", schema=MySchema)
```

---

## Creating a Custom Security Plugin

Add custom security validation:

```python
from strutex.plugins.base import SecurityPlugin, SecurityResult
from typing import Any, Dict

class CustomSecurityPlugin(SecurityPlugin, name="custom_security"):
    """Custom security validation."""

    def __init__(self, forbidden_words: list = None):
        self.forbidden_words = forbidden_words or []

    def validate_input(self, text: str) -> SecurityResult:
        """
        Validate input prompt before LLM call.

        Args:
            text: Input prompt to validate

        Returns:
            SecurityResult with valid=True/False and reason
        """
        # Check for forbidden words
        for word in self.forbidden_words:
            if word.lower() in text.lower():
                return SecurityResult(
                    valid=False,
                    reason=f"Forbidden word detected: {word}"
                )

        # Check for suspicious patterns
        if "ignore all previous" in text.lower():
            return SecurityResult(
                valid=False,
                reason="Potential injection attempt"
            )

        return SecurityResult(valid=True, text=text)

    def validate_output(self, data: Dict[str, Any]) -> SecurityResult:
        """
        Validate LLM output before returning.

        Args:
            data: Extracted data dict

        Returns:
            SecurityResult with valid=True/False and data
        """
        # Redact sensitive fields
        redacted = data.copy()

        for key in ["ssn", "password", "secret"]:
            if key in redacted:
                redacted[key] = "[REDACTED]"

        return SecurityResult(valid=True, data=redacted)
```

### Using Your Security Plugin

```python
from strutex import DocumentProcessor, GeminiProvider
from my_security import CustomSecurityPlugin

security = CustomSecurityPlugin(
    forbidden_words=["confidential", "internal"]
)

processor = DocumentProcessor(
    provider=GeminiProvider(),
    security=security
)

# Security validation is now active
result = processor.process("doc.pdf", "Extract", schema=MySchema)
```

---

## Plugin Discovery & Registration

### Auto-Registration (Recommended)

Simply inherit from base class with `name` argument:

```python
class MyProvider(Provider, name="my_provider"):
    pass
```

### Manual Registration

```python
from strutex.plugins.registry import PluginRegistry

PluginRegistry.register("provider", MyProvider, name="my_provider")
```

### List Registered Plugins

```python
from strutex.plugins.registry import PluginRegistry

# List all providers
providers = PluginRegistry.list_names("provider")
print(providers)  # ["gemini", "openai", "my_provider", ...]

# Get plugin info
info = PluginRegistry.get_plugin_info("provider", "my_provider")
print(info)  # {"name": "my_provider", "priority": 50, ...}
```

### Using CLI

```bash
# List all plugins
strutex plugins list

# Get plugin info
strutex plugins info provider my_provider

# Refresh plugin cache
strutex plugins refresh
```

---

## Entry Points (Package Distribution)

Distribute your plugin as a package:

```toml
# pyproject.toml
[project.entry-points."strutex.providers"]
my_provider = "my_package.providers:MyCustomProvider"

[project.entry-points."strutex.extractors"]
xml = "my_package.extractors:XMLExtractor"
```

After `pip install my_package`, the plugins are automatically discovered!

---

## Best Practices

| Practice                       | Why                           |
| ------------------------------ | ----------------------------- |
| Set `name` in class definition | Clear identification          |
| Add `priority` and `cost`      | Enables smart chain selection |
| Implement `health_check`       | Enables availability checks   |
| Add `version`                  | For compatibility tracking    |
| Use type hints                 | Better IDE support            |
| Add docstrings                 | Shows in `plugins info`       |

---

## Full Example: Azure OpenAI Provider

```python
from strutex.plugins.base import Provider
from typing import Any, Optional
import os

class AzureOpenAIProvider(Provider, name="azure_openai"):
    """Azure OpenAI provider for enterprise deployments."""

    priority = 30
    cost = 0.01
    version = "1.0.0"

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        deployment: str = "gpt-4",
        api_version: str = "2024-02-01"
    ):
        self.api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        self.endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment = deployment
        self.api_version = api_version

    def process(
        self,
        file_path: str,
        prompt: str,
        schema: Any,
        mime_type: str,
        **kwargs
    ) -> dict:
        from openai import AzureOpenAI

        client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.endpoint,
            api_version=self.api_version
        )

        # Read file and convert to base64 for images/PDFs
        # ... implementation ...

        response = client.chat.completions.create(
            model=self.deployment,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        import json
        return json.loads(response.choices[0].message.content)

    def health_check(self) -> bool:
        return bool(self.api_key and self.endpoint)
```

---

## Next Steps

| Want to...         | Go to...                                |
| ------------------ | --------------------------------------- |
| Learn hook system  | [Hooks Reference](hooks.md)             |
| See plugin API     | [Plugin System](plugins.md)             |
| Distribute package | [Entry Points](plugins.md#entry-points) |

</Parameter>
<parameter name="Complexity">5
