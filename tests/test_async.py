"""
Async tests for strutex providers and processor.

Tests:
- Provider.aprocess default behavior
- Custom async provider implementation
- Async error handling
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strutex.plugins import Provider, PluginRegistry
from strutex.plugins.base import ValidationResult


class TestAsyncProvider:
    """Test async provider functionality."""
    
    def setup_method(self):
        PluginRegistry.clear()
    
    @pytest.mark.asyncio
    async def test_aprocess_default_wraps_sync(self):
        """Default aprocess should call sync process."""
        call_log = []
        
        class SyncProvider(Provider):
            capabilities = ["test"]
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                call_log.append("sync_called")
                return {"result": "from_sync"}
        
        provider = SyncProvider()
        result = await provider.aprocess(
            file_path="test.pdf",
            prompt="test prompt",
            schema=None,
            mime_type="application/pdf"
        )
        
        assert "sync_called" in call_log
        assert result == {"result": "from_sync"}
    
    @pytest.mark.asyncio
    async def test_custom_aprocess_override(self):
        """Custom async provider should use overridden aprocess."""
        
        class AsyncProvider(Provider):
            capabilities = ["async"]
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                return {"result": "sync"}
            
            async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
                # Custom async implementation
                return {"result": "async", "file": file_path}
        
        provider = AsyncProvider()
        result = await provider.aprocess(
            file_path="document.pdf",
            prompt="extract",
            schema=None,
            mime_type="application/pdf"
        )
        
        assert result["result"] == "async"
        assert result["file"] == "document.pdf"
    
    @pytest.mark.asyncio
    async def test_aprocess_propagates_exceptions(self):
        """Async provider should propagate exceptions properly."""
        
        class FailingProvider(Provider):
            capabilities = []
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                raise ValueError("Intentional failure")
        
        provider = FailingProvider()
        
        with pytest.raises(ValueError, match="Intentional failure"):
            await provider.aprocess(
                file_path="test.pdf",
                prompt="test",
                schema=None,
                mime_type="application/pdf"
            )
    
    @pytest.mark.asyncio
    async def test_aprocess_with_kwargs(self):
        """Async provider should pass through kwargs."""
        received_kwargs = {}
        
        class KwargsProvider(Provider):
            capabilities = []
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                received_kwargs.update(kwargs)
                return {}
        
        provider = KwargsProvider()
        await provider.aprocess(
            file_path="test.pdf",
            prompt="test",
            schema=None,
            mime_type="application/pdf",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert received_kwargs.get("temperature") == 0.5
        assert received_kwargs.get("max_tokens") == 1000


class TestAsyncErrorHandling:
    """Test async error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_async_timeout_simulation(self):
        """Test handling of async timeout scenarios."""
        import asyncio
        
        class SlowProvider(Provider):
            capabilities = []
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                return {"result": "done"}
            
            async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
                await asyncio.sleep(0.1)
                return {"result": "async_done"}
        
        provider = SlowProvider()
        
        # Should complete normally
        result = await provider.aprocess(
            file_path="test.pdf",
            prompt="test",
            schema=None,
            mime_type="application/pdf"
        )
        
        assert result["result"] == "async_done"
    
    @pytest.mark.asyncio
    async def test_async_concurrent_calls(self):
        """Test concurrent async calls to provider."""
        import asyncio
        
        call_count = {"value": 0}
        
        class ConcurrentProvider(Provider):
            capabilities = ["async"]
            
            def process(self, file_path, prompt, schema, mime_type, **kwargs):
                return {}
            
            async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
                call_count["value"] += 1
                await asyncio.sleep(0.01)
                return {"call_id": call_count["value"]}
        
        provider = ConcurrentProvider()
        
        # Make concurrent calls
        tasks = [
            provider.aprocess("f1.pdf", "p1", None, "application/pdf"),
            provider.aprocess("f2.pdf", "p2", None, "application/pdf"),
            provider.aprocess("f3.pdf", "p3", None, "application/pdf"),
        ]
        
        results = await asyncio.gather(*tasks)
        
        assert len(results) == 3
        assert call_count["value"] == 3


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
