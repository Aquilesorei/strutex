
import os
import asyncio
from strutex import DocumentProcessor
from strutex.schemas import INVOICE_US

# Ensure you have set your API key
# os.environ["GOOGLE_API_KEY"] = "..."

def main():
    """Synchronous verification example."""
    print("--- Synchronous Verification ---")
    
    # Initialize processor (defaults to Gemini)
    processor = DocumentProcessor(provider="gemini", model_name="gemini-2.5-flash")
    
    # 1. Automatic Verification
    # This runs the extraction, then immediately runs a second pass 
    # to audit and correct the result.
    print("Processing with verification...")
    result = processor.process(
        file_path="invoice.pdf",  # Replace with actual file
        prompt="Extract invoice details",
        schema=INVOICE_US,
        verify=True  # 👈 Triggers self-correction
    )
    
    print("Verified Result:", result)

    # 2. Manual Verification
    # You can also verify an existing result manually
    print("\n--- Manual Verification ---")
    bad_result = {"invoice_number": "WRONG", "total": 0}
    
    verified_result = processor.verify(
        file_path="invoice.pdf",
        result=bad_result,
        schema=INVOICE_US
    )
    print("Fixed Result:", verified_result)

async def async_main():
    """Asynchronous verification example."""
    print("\n--- Asynchronous Verification ---")
    
    processor = DocumentProcessor(provider="gemini")
    
    # Async verification
    result = await processor.aprocess(
        file_path="invoice.pdf",
        prompt="Extract data",
        schema=INVOICE_US,
        verify=True
    )
    print("Async Verified Result:", result)

if __name__ == "__main__":
    # Create a dummy file if not exists for demo
    if not os.path.exists("invoice.pdf"):
        with open("invoice.pdf", "w") as f:
            f.write("Dummy PDF content")
            
    try:
        main()
        asyncio.run(async_main())
    except Exception as e:
        print(f"Error (expected if no API key/file): {e}")
