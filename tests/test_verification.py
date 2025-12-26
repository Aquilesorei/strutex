
"""
Tests for Verification / Self-Correction feature (v0.8.0).
"""

import pytest
import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from strutex.plugins import Provider, PluginRegistry
from strutex import DocumentProcessor
from strutex.types import Object, String, Number

class StatefuleMockProvider(Provider):
    """
    Mock provider that returns different results based on call count
    to simulate the extraction -> verification loop.
    """
    capabilities = ["mock"]
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.call_count = 0
        self.calls = []
        
    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        self.call_count += 1
        self.calls.append({
            "prompt": prompt,
            "call_count": self.call_count
        })
        
        # First call: Extraction (returns WRONG data)
        if self.call_count == 1:
            return {"total": 100, "status": "wrong"}
            
        # Second call: Verification (returns CORRECT data)
        # Verification prompt includes [EXTRACTED DATA TO VERIFY]
        if "[EXTRACTED DATA TO VERIFY]" in prompt:
            return {"total": 200, "status": "corrected"}
            
        return {"error": "Unexpected call sequence"}

    async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
        # Mirror sync logic for async
        return self.process(file_path, prompt, schema, mime_type, **kwargs)


class TestVerification:

    def setup_method(self):
        PluginRegistry.clear()
        # Create dummy file
        with open("dummy.pdf", "w") as f:
            f.write("test content")

    def teardown_method(self):
        if os.path.exists("dummy.pdf"):
            os.remove("dummy.pdf")

    def test_verify_flag_triggers_loop(self):
        """Test that verify=True triggers a second call."""
        provider = StatefuleMockProvider()
        processor = DocumentProcessor(provider=provider)
        
        schema = Object(properties={"total": Number(), "status": String()})
        
        # When processing with verify=True
        final_result = processor.process(
            file_path="dummy.pdf",
            prompt="Extract",
            schema=schema,
            verify=True
        )
        
        # Check provider was called twice
        assert provider.call_count == 2
        
        # Check first call (Extraction)
        assert "Extract" in provider.calls[0]["prompt"]
        assert "[EXTRACTED DATA TO VERIFY]" not in provider.calls[0]["prompt"]
        
        # Check second call (Verification)
        assert "[EXTRACTED DATA TO VERIFY]" in provider.calls[1]["prompt"]
        assert "wrong" in provider.calls[1]["prompt"]  # It sees the bad data
        
        # Result should be the corrected one
        assert final_result["total"] == 200
        assert final_result["status"] == "corrected"

    @pytest.mark.asyncio
    async def test_async_verify_flag(self):
        """Test verify=True in aprocess."""
        provider = StatefuleMockProvider()
        processor = DocumentProcessor(provider=provider)
        
        schema = Object(properties={"total": Number(), "status": String()})
        
        final_result = await processor.aprocess(
            file_path="dummy.pdf",
            prompt="Extract",
            schema=schema,
            verify=True
        )
        
        assert provider.call_count == 2
        assert final_result["status"] == "corrected"

    def test_manual_verify_method(self):
        """Test explicit verify() method."""
        provider = StatefuleMockProvider()
        processor = DocumentProcessor(provider=provider)
        
        # Manually set call count so next call acts as "Second call"
        # Only needed if provider logic depends strictly on count, 
        # but here it also checks prompt content.
        
        bad_result = {"total": 100, "status": "wrong"}
        
        # Call verify directly
        # Must provide schema because process() requires it
        schema = Object(properties={"total": Number(), "status": String()})
        
        corrected = processor.verify(
            file_path="dummy.pdf",
            result=bad_result,
            schema=schema
        )
        
        # ... logic ...
        pass

class VerifyProvider(Provider):
    """Smarter mock that checks prompt content primarily."""
    capabilities = ["mock"]
    
    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        if "[EXTRACTED DATA TO VERIFY]" in prompt:
            return {"status": "corrected"}
        return {"status": "wrong"}

class TestManualVerification:
    
    def setup_method(self):
        with open("dummy.pdf", "w") as f:
            f.write("test content")

    def teardown_method(self):
        if os.path.exists("dummy.pdf"):
            os.remove("dummy.pdf")

    def test_verify_call(self):
        provider = VerifyProvider()
        processor = DocumentProcessor(provider=provider)
        
        bad_result = {"status": "wrong"}
        schema = Object(properties={"status": String()})
        
        result = processor.verify(
            file_path="dummy.pdf",
            result=bad_result,
            schema=schema
        )
        
        assert result["status"] == "corrected"

if __name__ == "__main__":
    # Create dummy file for file existence check in processor
    if not os.path.exists("dummy.pdf"):
        with open("dummy.pdf", "w") as f:
            f.write("test")
    try:
        pytest.main([__file__, "-v"])
    finally:
        if os.path.exists("dummy.pdf"):
            os.remove("dummy.pdf")
