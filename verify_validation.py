import asyncio
from unittest.mock import MagicMock
from strutex import DocumentProcessor, Object, String, Provider

# Mock Provider that returns wrong data first, then corrects it
class CorrectionProvider(Provider):
    def __init__(self):
        self.call_count = 0

    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        self.call_count += 1
        if self.call_count == 1:
            # First call: incorrect data
            return {"invoice_number": "WRONG-123", "total": 100}
        else:
            # Second call (verification): correct data
            # Check if prompt contains verification instructions
            if "verify" in prompt.lower() or "audit" in prompt.lower():
                return {"invoice_number": "CORRECT-999", "total": 100}
            return {"invoice_number": "STILL-WRONG", "total": 100}

    async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
        return self.process(file_path, prompt, schema, mime_type, **kwargs)

def test_verification():
    print("\n--- Testing Verification Workflow ---")
    provider = CorrectionProvider()
    processor = DocumentProcessor(provider=provider)
    
    # Create dummy file
    with open("dummy.pdf", "w") as f: f.write("dummy")
    
    schema = Object(properties={"invoice_number": String(), "total": String()})
    
    # 1. Process without verification
    result = processor.process("dummy.pdf", "Extract", schema)
    print("Run 1 Result:", result)
    assert result["invoice_number"] == "WRONG-123"
    
    # Reset provider
    provider.call_count = 0
    
    # 2. Process WITH verification
    print("Running with verify=True...")
    result_verified = processor.process("dummy.pdf", "Extract", schema, verify=True)
    print("Run 2 Result:", result_verified)
    
    assert result_verified["invoice_number"] == "CORRECT-999"
    assert provider.call_count == 2 # 1 extraction + 1 verification
    print("Verification Logic Passed!")

    # 3. Test Async Verification
    async def async_test():
        print("\n--- Async Verification ---")
        provider.call_count = 0
        result_async = await processor.aprocess("dummy.pdf", "Extract", schema, verify=True)
        print("Async Result:", result_async)
        assert result_async["invoice_number"] == "CORRECT-999"
        assert provider.call_count == 2
        print("Async Verification Passed!")

    import os
    asyncio.run(async_test())
    os.remove("dummy.pdf")

if __name__ == "__main__":
    test_verification()
