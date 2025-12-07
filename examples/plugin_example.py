#!/usr/bin/env python3
"""
Plugin system example.

Demonstrates:
- Registering custom plugins
- Using the plugin registry
- Creating custom providers
- Plugin discovery
"""

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pyapu.plugins import (
    PluginRegistry,
    register,
    Provider,
    Extractor,
    Validator,
    ValidationResult,
    Postprocessor
)
from pyapu.types import Schema


def demo_plugin_registry():
    """Demonstrate basic registry operations."""
    print("=" * 50)
    print("PLUGIN REGISTRY BASICS")
    print("=" * 50)
    
    # Clear registry for demo
    PluginRegistry.clear()
    
    # Manual registration
    class MyPlugin:
        pass
    
    PluginRegistry.register("custom", "my_plugin", MyPlugin)
    
    # Retrieve
    retrieved = PluginRegistry.get("custom", "my_plugin")
    print(f"Retrieved: {retrieved}")
    print(f"Same class: {retrieved is MyPlugin}")
    
    # List plugins
    PluginRegistry.register("custom", "another_plugin", MyPlugin)
    all_custom = PluginRegistry.list("custom")
    print(f"\nAll custom plugins: {list(all_custom.keys())}")
    
    # List types
    PluginRegistry.register("validator", "test", MyPlugin)
    types = PluginRegistry.list_types()
    print(f"Plugin types: {types}")


def demo_decorator_registration():
    """Demonstrate decorator-based registration."""
    print("\n" + "=" * 50)
    print("DECORATOR REGISTRATION")
    print("=" * 50)
    
    PluginRegistry.clear()
    
    # Auto-name from class name
    @register("provider")
    class AutoNamedProvider(Provider):
        def process(self, *args, **kwargs):
            return {"source": "auto-named"}
    
    # Explicit name
    @register("provider", name="custom_gemini")
    class MyGeminiProvider(Provider):
        def process(self, *args, **kwargs):
            return {"source": "custom-gemini"}
    
    print(f"Auto-named: {PluginRegistry.get('provider', 'autonamedprovider')}")
    print(f"Explicit name: {PluginRegistry.get('provider', 'custom_gemini')}")
    print(f"All providers: {list(PluginRegistry.list('provider').keys())}")


def demo_custom_provider():
    """Demonstrate creating a custom provider."""
    print("\n" + "=" * 50)
    print("CUSTOM PROVIDER")
    print("=" * 50)
    
    PluginRegistry.clear()
    
    @register("provider")
    class MockProvider(Provider):
        """A mock provider for testing."""
        
        capabilities = ["mock", "testing"]
        
        def __init__(self, response_data: dict = None):
            self.response_data = response_data or {"mock": True}
        
        def process(self, file_path, prompt, schema, mime_type, **kwargs):
            print(f"  MockProvider processing: {file_path}")
            print(f"  MIME type: {mime_type}")
            return self.response_data
    
    # Use the provider
    provider = MockProvider(response_data={"invoice_number": "MOCK-001"})
    
    print(f"Capabilities: {provider.capabilities}")
    print(f"Has 'mock': {provider.has_capability('mock')}")
    print(f"Has 'vision': {provider.has_capability('vision')}")
    
    result = provider.process("test.pdf", "Extract data", None, "application/pdf")
    print(f"Result: {result}")


def demo_custom_extractor():
    """Demonstrate creating a custom extractor."""
    print("\n" + "=" * 50)
    print("CUSTOM EXTRACTOR")
    print("=" * 50)
    
    @register("extractor")
    class MarkdownExtractor(Extractor):
        """Extracts text from markdown files."""
        
        supported_mime_types = ["text/markdown", "text/x-markdown"]
        
        def extract(self, file_path: str) -> str:
            with open(file_path, "r") as f:
                content = f.read()
            
            # Simple markdown stripping (just for demo)
            import re
            # Remove headers markers
            content = re.sub(r'^#+\s*', '', content, flags=re.MULTILINE)
            # Remove bold/italic
            content = re.sub(r'\*+([^*]+)\*+', r'\1', content)
            
            return content
    
    extractor = MarkdownExtractor()
    print(f"Supported types: {extractor.supported_mime_types}")
    print(f"Can handle text/markdown: {extractor.can_handle('text/markdown')}")
    print(f"Can handle application/pdf: {extractor.can_handle('application/pdf')}")


def demo_custom_validator():
    """Demonstrate creating a custom validator."""
    print("\n" + "=" * 50)
    print("CUSTOM VALIDATOR")
    print("=" * 50)
    
    @register("validator")
    class InvoiceValidator(Validator):
        """Validates invoice data with business rules."""
        
        def validate(self, data, schema=None):
            issues = []
            
            # Check required fields
            if not data.get("invoice_number"):
                issues.append("Missing invoice number")
            
            # Check total is positive
            total = data.get("total", 0)
            if total <= 0:
                issues.append(f"Invalid total: {total}")
            
            # Verify line items sum
            items = data.get("items", [])
            if items:
                items_total = sum(item.get("total", 0) for item in items)
                if abs(items_total - total) > 0.01:
                    issues.append(f"Line items total ({items_total}) != invoice total ({total})")
            
            return ValidationResult(
                valid=len(issues) == 0,
                data=data,
                issues=issues
            )
    
    validator = InvoiceValidator()
    
    # Valid data
    valid_data = {
        "invoice_number": "INV-001",
        "total": 100.00,
        "items": [{"total": 100.00}]
    }
    result = validator.validate(valid_data)
    print(f"Valid data: {result.valid}, Issues: {result.issues}")
    
    # Invalid data
    invalid_data = {
        "invoice_number": "",
        "total": -50,
        "items": []
    }
    result = validator.validate(invalid_data)
    print(f"Invalid data: {result.valid}")
    print(f"Issues: {result.issues}")


def demo_custom_postprocessor():
    """Demonstrate creating a custom postprocessor."""
    print("\n" + "=" * 50)
    print("CUSTOM POSTPROCESSOR")
    print("=" * 50)
    
    @register("postprocessor")
    class DateNormalizer(Postprocessor):
        """Normalizes date formats to ISO 8601."""
        
        def __init__(self, date_fields: list = None):
            self.date_fields = date_fields or ["date", "invoice_date", "due_date"]
        
        def process(self, data):
            import re
            
            result = data.copy()
            
            for field in self.date_fields:
                if field in result and result[field]:
                    # Convert DD.MM.YYYY to YYYY-MM-DD
                    match = re.match(r'(\d{2})\.(\d{2})\.(\d{4})', str(result[field]))
                    if match:
                        d, m, y = match.groups()
                        result[field] = f"{y}-{m}-{d}"
            
            return result
    
    normalizer = DateNormalizer()
    
    data = {
        "invoice_number": "INV-001",
        "date": "15.01.2024",
        "due_date": "30.01.2024"
    }
    
    normalized = normalizer.process(data)
    print(f"Original date: {data['date']}")
    print(f"Normalized date: {normalized['date']}")
    print(f"Original due_date: {data['due_date']}")
    print(f"Normalized due_date: {normalized['due_date']}")


def demo_using_with_processor():
    """Show how to use custom providers with DocumentProcessor."""
    print("\n" + "=" * 50)
    print("USING WITH DOCUMENT PROCESSOR")
    print("=" * 50)
    
    from pyapu import DocumentProcessor
    
    PluginRegistry.clear()
    
    # Register a mock provider
    @register("provider", name="test_provider")
    class TestProvider(Provider):
        def __init__(self, api_key=None, model=None):
            self.api_key = api_key
            self.model = model
        
        def process(self, file_path, prompt, schema, mime_type, **kwargs):
            return {
                "invoice_number": "TEST-001",
                "total": 999.99
            }
    
    # Use by name
    processor = DocumentProcessor(provider="test_provider")
    print("Created processor with custom provider by name")
    
    # Or pass instance directly
    provider = TestProvider()
    processor2 = DocumentProcessor(provider=provider)
    print("Created processor with provider instance")


if __name__ == "__main__":
    demo_plugin_registry()
    demo_decorator_registration()
    demo_custom_provider()
    demo_custom_extractor()
    demo_custom_validator()
    demo_custom_postprocessor()
    demo_using_with_processor()
