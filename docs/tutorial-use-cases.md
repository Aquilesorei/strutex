# Use Cases

Complete working examples for common document types.

---

## Invoice Extraction

### Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class LineItem(BaseModel):
    description: str
    quantity: int
    unit_price: float
    total: float

class Invoice(BaseModel):
    invoice_number: str
    vendor_name: str
    vendor_address: Optional[str] = None
    customer_name: str
    customer_address: Optional[str] = None
    date: str
    due_date: Optional[str] = None
    items: List[LineItem]
    subtotal: float
    tax: Optional[float] = None
    discount: Optional[float] = None
    total: float
    payment_terms: Optional[str] = None
```

### Extraction

```python
from strutex import DocumentProcessor, GeminiProvider, MemoryCache

processor = DocumentProcessor(
    provider=GeminiProvider(),
    cache=MemoryCache(ttl=3600)
)

result = processor.process(
    file_path="invoice.pdf",
    prompt="""
    Extract all invoice details including:
    - Invoice number and dates
    - Vendor and customer information
    - All line items with quantities and prices
    - Subtotal, tax, and total
    """,
    model=Invoice,
    verify=True  # Self-correction for accuracy
)

print(f"Invoice #{result.invoice_number}")
print(f"Vendor: {result.vendor_name}")
print(f"Total: ${result.total:.2f}")
for item in result.items:
    print(f"  - {item.description}: ${item.total:.2f}")
```

### Or Use Built-in Schema

```python
from strutex.schemas import INVOICE_US

result = processor.process(
    file_path="invoice.pdf",
    prompt="Extract invoice details",
    schema=INVOICE_US
)
```

---

## Receipt Extraction

### Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class PurchasedItem(BaseModel):
    name: str
    quantity: int = 1
    price: float

class Receipt(BaseModel):
    store_name: str
    store_address: Optional[str] = None
    date: str
    time: Optional[str] = None
    items: List[PurchasedItem]
    subtotal: float
    tax: float
    total: float
    payment_method: Optional[str] = None
    card_last_four: Optional[str] = None
```

### Extraction

```python
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

result = processor.process(
    file_path="receipt.jpg",  # Works with images!
    prompt="""
    Extract receipt details:
    - Store name and address
    - Date and time
    - All purchased items with prices
    - Tax and total
    - Payment method
    """,
    model=Receipt
)

print(f"Store: {result.store_name}")
print(f"Date: {result.date}")
print(f"Total: ${result.total:.2f}")
```

---

## Resume/CV Extraction

### Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: Optional[int] = None
    gpa: Optional[float] = None

class Experience(BaseModel):
    company: str
    title: str
    start_date: str
    end_date: Optional[str] = None  # None = current
    responsibilities: List[str]

class Resume(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    location: Optional[str] = None
    summary: Optional[str] = None
    skills: List[str]
    education: List[Education]
    experience: List[Experience]
    certifications: Optional[List[str]] = None
    languages: Optional[List[str]] = None
```

### Extraction

```python
from strutex import DocumentProcessor, GeminiProvider

processor = DocumentProcessor(provider=GeminiProvider())

result = processor.process(
    file_path="resume.pdf",
    prompt="""
    Extract all resume information:
    - Contact details
    - Professional summary
    - Skills (as a list)
    - Education history
    - Work experience with responsibilities
    - Certifications and languages
    """,
    model=Resume
)

print(f"Candidate: {result.name}")
print(f"Email: {result.email}")
print(f"Skills: {', '.join(result.skills[:5])}...")
print(f"Experience: {len(result.experience)} positions")
```

---

## Purchase Order Extraction

### Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class POLineItem(BaseModel):
    sku: Optional[str] = None
    description: str
    quantity: int
    unit_price: float
    total: float

class PurchaseOrder(BaseModel):
    po_number: str
    date: str
    vendor_name: str
    vendor_address: Optional[str] = None
    ship_to_address: str
    bill_to_address: Optional[str] = None
    items: List[POLineItem]
    subtotal: float
    shipping: Optional[float] = None
    tax: Optional[float] = None
    total: float
    delivery_date: Optional[str] = None
    payment_terms: Optional[str] = None
```

### Extraction

```python
result = processor.process(
    file_path="purchase_order.pdf",
    prompt="Extract purchase order details",
    model=PurchaseOrder,
    verify=True
)

print(f"PO#: {result.po_number}")
print(f"Vendor: {result.vendor_name}")
print(f"Total: ${result.total:.2f}")
```

---

## Medical Records

### Schema

```python
from pydantic import BaseModel
from typing import List, Optional

class Medication(BaseModel):
    name: str
    dosage: str
    frequency: str
    start_date: Optional[str] = None

class MedicalRecord(BaseModel):
    patient_name: str
    date_of_birth: Optional[str] = None
    visit_date: str
    provider_name: str
    diagnosis: List[str]
    medications: List[Medication]
    notes: Optional[str] = None
    follow_up: Optional[str] = None
```

### Extraction with Security

```python
from strutex import DocumentProcessor, GeminiProvider
from strutex.security import SecurityChain, PIIRedactor

# Add PII redaction for HIPAA compliance
security = SecurityChain([PIIRedactor()])

processor = DocumentProcessor(
    provider=GeminiProvider(),
    security=security
)

result = processor.process(
    file_path="medical_record.pdf",
    prompt="Extract medical visit information",
    model=MedicalRecord
)

# PII is automatically redacted
```

---

## Batch Processing Multiple Types

```python
from strutex import DocumentProcessor, GeminiProvider
from pathlib import Path

processor = DocumentProcessor(provider=GeminiProvider())

# Schema mapping
SCHEMAS = {
    "invoice": Invoice,
    "receipt": Receipt,
    "resume": Resume,
}

def process_document(file_path: str, doc_type: str):
    schema = SCHEMAS.get(doc_type)
    if not schema:
        raise ValueError(f"Unknown document type: {doc_type}")

    return processor.process(
        file_path=file_path,
        prompt=f"Extract all {doc_type} information",
        model=schema
    )

# Process different documents
invoice = process_document("invoice.pdf", "invoice")
receipt = process_document("receipt.jpg", "receipt")
resume = process_document("cv.pdf", "resume")
```

---

## Next Steps

| Want to...       | Go to...                                     |
| ---------------- | -------------------------------------------- |
| Optimize prompts | [Prompt Engineering](tutorial-prompts.md)    |
| Add validation   | [Validation](tutorial-validation.md)         |
| Handle errors    | [Error Handling](tutorial-error-handling.md) |
