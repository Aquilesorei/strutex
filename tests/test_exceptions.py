"""
Tests for exception hierarchy.
"""

import pytest
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strutex.exceptions import (
    StrutexError,
    ProviderError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    ExtractionError,
    DocumentParseError,
    SchemaError,
    ValidationError,
    SchemaValidationError,
    ConfigurationError,
    PluginError,
    CacheError,
    SecurityError,
    InjectionDetectedError,
    TimeoutError,
)


class TestStrutexError:
    """Tests for base StrutexError."""
    
    def test_basic_message(self):
        """Test basic error message."""
        err = StrutexError("Something went wrong")
        assert str(err) == "Something went wrong"
        assert err.message == "Something went wrong"
    
    def test_with_details(self):
        """Test error with details dict."""
        err = StrutexError("Failed", details={"file": "test.pdf", "line": 42})
        assert "test.pdf" in str(err)
        assert err.details["file"] == "test.pdf"
    
    def test_all_inherit_from_base(self):
        """Test all exceptions inherit from StrutexError."""
        exceptions = [
            ProviderError("test"),
            RateLimitError(),
            AuthenticationError(),
            ExtractionError("test"),
            ValidationError("test"),
            ConfigurationError("test"),
            CacheError("test"),
            SecurityError("test"),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, StrutexError)


class TestProviderErrors:
    """Tests for provider error hierarchy."""
    
    def test_provider_error_attributes(self):
        """Test ProviderError has expected attributes."""
        err = ProviderError(
            "API call failed",
            provider="openai",
            status_code=500,
            retryable=True
        )
        assert err.provider == "openai"
        assert err.status_code == 500
        assert err.retryable is True
    
    def test_rate_limit_defaults(self):
        """Test RateLimitError has sensible defaults."""
        err = RateLimitError()
        assert err.status_code == 429
        assert err.retryable is True
        assert "Rate limit" in str(err)
    
    def test_rate_limit_retry_after(self):
        """Test RateLimitError with retry_after."""
        err = RateLimitError(retry_after=30.0, provider="gemini")
        assert err.retry_after == 30.0
        assert err.provider == "gemini"
    
    def test_auth_error(self):
        """Test AuthenticationError."""
        err = AuthenticationError(provider="openai")
        assert err.status_code == 401
        assert err.retryable is False
    
    def test_model_not_found(self):
        """Test ModelNotFoundError."""
        err = ModelNotFoundError(model="gpt-5", provider="openai")
        assert err.model == "gpt-5"
        assert "gpt-5" in str(err)
        assert err.status_code == 404


class TestExtractionErrors:
    """Tests for extraction error hierarchy."""
    
    def test_extraction_error(self):
        """Test ExtractionError attributes."""
        err = ExtractionError(
            "Failed to extract",
            file_path="/path/to/doc.pdf",
            stage="llm"
        )
        assert err.file_path == "/path/to/doc.pdf"
        assert err.stage == "llm"
    
    def test_document_parse_error(self):
        """Test DocumentParseError."""
        err = DocumentParseError(
            "Cannot read PDF",
            file_path="corrupt.pdf",
            mime_type="application/pdf"
        )
        assert err.mime_type == "application/pdf"
        assert err.stage == "parsing"
    
    def test_schema_error(self):
        """Test SchemaError."""
        err = SchemaError("Invalid schema", schema_type="Object")
        assert err.schema_type == "Object"
        assert err.stage == "schema"


class TestValidationErrors:
    """Tests for validation error hierarchy."""
    
    def test_validation_error_issues(self):
        """Test ValidationError with issues list."""
        err = ValidationError(
            "Validation failed",
            issues=["field1: required", "field2: wrong type", "field3: invalid"]
        )
        assert len(err.issues) == 3
        # Should show first 3 issues in string
        assert "field1" in str(err)
    
    def test_validation_error_many_issues(self):
        """Test ValidationError truncates many issues."""
        err = ValidationError(
            "Validation failed",
            issues=["issue1", "issue2", "issue3", "issue4", "issue5"]
        )
        # Should mention "+2 more"
        assert "+2 more" in str(err)
    
    def test_validation_error_with_data(self):
        """Test ValidationError stores failed data."""
        data = {"name": "John", "age": "invalid"}
        err = ValidationError("Type mismatch", data=data)
        assert err.data == data
    
    def test_schema_validation_error_inherits(self):
        """Test SchemaValidationError inherits from ValidationError."""
        err = SchemaValidationError("Schema mismatch", issues=["missing field"])
        assert isinstance(err, ValidationError)
        assert isinstance(err, StrutexError)


class TestConfigErrors:
    """Tests for configuration error hierarchy."""
    
    def test_configuration_error(self):
        """Test ConfigurationError."""
        err = ConfigurationError("Invalid config", config_key="api_key")
        assert err.config_key == "api_key"
    
    def test_plugin_error(self):
        """Test PluginError."""
        err = PluginError(
            "Plugin failed to load",
            plugin_name="my_plugin",
            plugin_type="provider"
        )
        assert err.plugin_name == "my_plugin"
        assert err.plugin_type == "provider"


class TestSecurityErrors:
    """Tests for security error hierarchy."""
    
    def test_security_error(self):
        """Test SecurityError."""
        err = SecurityError("Security check failed")
        assert isinstance(err, StrutexError)
    
    def test_injection_detected(self):
        """Test InjectionDetectedError."""
        err = InjectionDetectedError(pattern="IGNORE PREVIOUS")
        assert err.pattern == "IGNORE PREVIOUS"
        assert "injection" in str(err).lower()


class TestCacheErrors:
    """Tests for cache errors."""
    
    def test_cache_error(self):
        """Test CacheError."""
        err = CacheError("Cache miss", operation="get")
        assert err.operation == "get"


class TestTimeoutError:
    """Tests for timeout error."""
    
    def test_timeout_error(self):
        """Test TimeoutError."""
        err = TimeoutError(timeout_seconds=30.0)
        assert err.timeout_seconds == 30.0
        assert "timed out" in str(err).lower()


class TestExceptionCatching:
    """Tests for catching exceptions at different levels."""
    
    def test_catch_all_strutex(self):
        """Test catching all Strutex errors."""
        errors = [
            ProviderError("test"),
            ValidationError("test"),
            CacheError("test"),
        ]
        
        for err in errors:
            try:
                raise err
            except StrutexError as e:
                assert e.message == "test"
    
    def test_catch_provider_subclasses(self):
        """Test catching provider error subclasses."""
        errors = [
            RateLimitError(),
            AuthenticationError(),
            ModelNotFoundError("gpt-5"),
        ]
        
        for err in errors:
            try:
                raise err
            except ProviderError:
                pass  # Should be caught


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
