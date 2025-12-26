from strutex import DocumentProcessor, Object, String, ProcessingContext
import os

# Create dummy file
with open("test.txt", "w") as f: f.write("dummy")

# Mock Provider with usage stats
class UsageProvider:
    def process(self, *args, **kwargs):
        return {
            "data": "extracted",
            "_usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
                "total_cost": 0.002
            }
        }

    async def aprocess(self, *args, **kwargs):
        return {
            "data": "extracted",
            "_usage": {
                "input_tokens": 100,
                "output_tokens": 50,
                "total_tokens": 150,
                "total_cost": 0.002
            }
        }

def test_usage_tracking():
    print("\n--- Testing Usage Tracking ---")
    ctx = ProcessingContext()
    processor = DocumentProcessor(provider=UsageProvider())
    
    # Step 1
    ctx.extract(processor, "test.txt", "prompt", Object(properties={"data": String()}))
    
    # Step 2
    ctx.extract(processor, "test.txt", "prompt", Object(properties={"data": String()}))
    
    print(f"Total tokens: {ctx.total_tokens}")
    print(f"Total cost: {ctx.total_cost}")
    
    assert ctx.total_tokens == 300
    assert ctx.total_cost == 0.004
    
    # Check history
    assert ctx.history[0].metadata["usage"]["total_tokens"] == 150
    
    print("Usage Tracking Passed!")
    os.remove("test.txt")

if __name__ == "__main__":
    test_usage_tracking()
