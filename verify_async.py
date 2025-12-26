import asyncio
import os
import time
from unittest.mock import MagicMock, AsyncMock
from strutex import DocumentProcessor, Object, String

# Mock Provider
class MockProvider:
    def process(self, file_path, prompt, schema, mime_type, **kwargs):
        time.sleep(0.1)  # Simulate delay
        return {"status": "processed", "file": file_path}

    async def aprocess(self, file_path, prompt, schema, mime_type, **kwargs):
        await asyncio.sleep(0.1)  # Simulate async delay
        return {"status": "aprocessed", "file": file_path}

# Test Schema
schema = Object(properties={"status": String(), "file": String()})

def test_batch_processing():
    print("\n--- Testing Sync Batch Processing ---")
    provider = MockProvider()
    processor = DocumentProcessor(provider=provider)
    
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    # Mock existence
    with open("doc1.pdf", "w") as f: f.write("dummy")
    with open("doc2.pdf", "w") as f: f.write("dummy")
    with open("doc3.pdf", "w") as f: f.write("dummy")
    
    start = time.time()
    batch_ctx = processor.process_batch(files, "Extract", schema, max_workers=3)
    duration = time.time() - start
    
    print(f"Processed {batch_ctx.progress} files in {duration:.4f}s")
    assert batch_ctx.progress == 3
    assert duration < 0.2  # Should be parallel (0.1s + overhead)
    
    # Cleanup
    for f in files: os.remove(f)
    print("Sync Batch Passed!")

async def test_async_batch_processing():
    print("\n--- Testing Async Batch Processing ---")
    provider = MockProvider()
    processor = DocumentProcessor(provider=provider)
    
    files = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
    for f in files: 
        with open(f, "w") as file: file.write("dummy")
        
    start = time.time()
    batch_ctx = await processor.aprocess_batch(files, "Extract", schema, max_concurrency=3)
    duration = time.time() - start
    
    print(f"Processed {batch_ctx.progress} files in {duration:.4f}s")
    assert batch_ctx.progress == 3
    assert duration < 0.2
    
    for f in files: os.remove(f)
    print("Async Batch Passed!")

if __name__ == "__main__":
    test_batch_processing()
    asyncio.run(test_async_batch_processing())
