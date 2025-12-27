# Prompt Engineering

Write better prompts for more accurate extraction using the StructuredPrompt builder.

---

## The StructuredPrompt Builder

Strutex provides a fluent API for building well-organized prompts:

```python
from strutex.prompts import StructuredPrompt

prompt = (
    StructuredPrompt("You are an expert invoice data extractor.")
    .add_general_rule(
        "Strict data fidelity: do not invent values.",
        "Use ISO date format: YYYY-MM-DD.",
        "If a field is missing, return null."
    )
    .add_field_rule(
        "invoice_number",
        "Must match format: INV-XXXX or similar.",
        "Found at top of document.",
        critical=True
    )
    .add_field_rule(
        "total",
        "Final amount after tax and discounts.",
        "Must be numeric.",
        critical=True
    )
    .add_output_guideline(
        "Output valid JSON only.",
        "No markdown formatting.",
        "No code blocks."
    )
    .compile()
)

print(prompt)
```

**Output:**

```
You are an expert invoice data extractor.

### 1. General Principles
- Strict data fidelity: do not invent values.
- Use ISO date format: YYYY-MM-DD.
- If a field is missing, return null.

### 2. Field Rules

**invoice_number**:
- **CRITICAL**: Must match format: INV-XXXX or similar.
- **CRITICAL**: Found at top of document.

**total**:
- **CRITICAL**: Final amount after tax and discounts.
- **CRITICAL**: Must be numeric.

### 3. Output Format
- Output valid JSON only.
- No markdown formatting.
- No code blocks.
```

---

## Using with DocumentProcessor

```python
from strutex import DocumentProcessor, GeminiProvider
from strutex.prompts import StructuredPrompt

# Build the prompt
prompt = (
    StructuredPrompt()
    .add_general_rule("Extract all visible data.", "No guessing.")
    .add_field_rule("vendor_name", "Company issuing the invoice.")
    .add_field_rule("total", "Final amount due.", critical=True)
    .compile()
)

# Use with processor
processor = DocumentProcessor(provider=GeminiProvider())
result = processor.process(
    file_path="invoice.pdf",
    prompt=prompt,  # Use compiled prompt
    model=Invoice
)
```

---

## StructuredPrompt API

### Constructor

```python
prompt = StructuredPrompt(
    persona="You are a highly accurate AI Data Extraction Assistant."
)
```

### add_general_rule(\*rules)

Add high-level extraction principles:

```python
prompt.add_general_rule(
    "No guessing: only extract visible data.",
    "Dates must be in YYYY-MM-DD format.",
    "Currency amounts should exclude symbols."
)
```

### add_field_rule(field_name, \*rules, critical=False)

Add field-specific rules. Use `critical=True` to emphasize:

```python
prompt.add_field_rule(
    "invoice_number",
    "Usually at top-right of document.",
    "Format: INV-XXXX or #XXXX.",
    critical=True  # Adds **CRITICAL** prefix
)
```

### add_output_guideline(\*guidelines)

Specify output format requirements:

```python
prompt.add_output_guideline(
    "Return valid JSON only.",
    "No markdown code blocks.",
    "No explanatory text."
)
```

### compile()

Build the final prompt string:

```python
final_prompt = prompt.compile()
# Or use directly: str(prompt)
```

### from_schema(schema) — Auto-Generate from Pydantic

Create a prompt with field rules auto-generated from Pydantic Field descriptions:

```python
from pydantic import BaseModel, Field
from strutex.prompts import StructuredPrompt

class Invoice(BaseModel):
    invoice_number: str = Field(description="Unique invoice ID")
    total: float = Field(description="Final amount due")
    tax: float = Field(default=0, description="Tax amount if applicable")

# Auto-generate field rules from schema
prompt = StructuredPrompt.from_schema(Invoice)

# Add additional rules
prompt.add_general_rule("Use ISO dates", "No guessing")

print(prompt.compile())
```

**Output:**

```
You are a highly accurate AI Data Extraction Assistant.

### 1. General Principles
- Use ISO dates
- No guessing

### 2. Field Rules

**invoice_number**:
- **CRITICAL**: Unique invoice ID

**total**:
- **CRITICAL**: Final amount due

**tax**:
- Tax amount if applicable

### 3. Output Format
- Output valid JSON only. No markdown.
```

**Note:** Required fields are automatically marked **CRITICAL**, optional fields are not.

---

## Prompt Templates

### Invoice Template

```python
from strutex.prompts import StructuredPrompt

INVOICE_PROMPT = (
    StructuredPrompt("You are an expert invoice data extractor.")
    .add_general_rule(
        "Extract ALL visible data—do not invent values.",
        "Use ISO 8601 dates: YYYY-MM-DD.",
        "For missing fields, return null.",
        "Amounts should be numeric (no currency symbols)."
    )
    .add_field_rule(
        "invoice_number",
        "The unique invoice identifier.",
        "Usually at top of document.",
        critical=True
    )
    .add_field_rule(
        "line_items",
        "Extract ALL line items.",
        "Each item needs: description, quantity, unit_price, total.",
        "If item spans multiple lines, combine."
    )
    .add_field_rule(
        "total",
        "Final amount after tax and discounts.",
        "Verify: subtotal + tax - discount = total.",
        critical=True
    )
    .add_output_guideline("Valid JSON only. No markdown.")
    .compile()
)
```

### Receipt Template

```python
RECEIPT_PROMPT = (
    StructuredPrompt("You are a receipt OCR specialist.")
    .add_general_rule(
        "Handle low-quality scans gracefully.",
        "Prices may be formatted as $X.XX or X.XX.",
        "Skip separator lines (----, ====)."
    )
    .add_field_rule(
        "store_name",
        "Usually at the very top, often in large text."
    )
    .add_field_rule(
        "items",
        "Each purchased item with name and price.",
        "Quantity defaults to 1 if not shown."
    )
    .add_field_rule(
        "total",
        "Final amount paid.",
        "Usually at bottom, often labeled 'TOTAL' or 'AMOUNT DUE'.",
        critical=True
    )
    .compile()
)
```

### Resume Template

```python
RESUME_PROMPT = (
    StructuredPrompt("You are an expert resume parser.")
    .add_general_rule(
        "Extract structured data from resume/CV.",
        "Preserve original language for names and companies.",
        "Dates should be YYYY-MM format."
    )
    .add_field_rule(
        "name",
        "Full name, usually the largest text at top.",
        critical=True
    )
    .add_field_rule(
        "experience",
        "List all work experience.",
        "Each entry: company, title, start_date, end_date, responsibilities.",
        "Current jobs have end_date = null."
    )
    .add_field_rule(
        "skills",
        "Technical and soft skills as a list.",
        "May be comma-separated, bulleted, or in a table."
    )
    .compile()
)
```

---

## Handling Edge Cases

### Ambiguous Dates

```python
prompt = (
    StructuredPrompt()
    .add_field_rule(
        "date",
        "Convert to YYYY-MM-DD format.",
        "If only month/year (e.g., 'March 2024'), use 01 for day.",
        "If relative (e.g., 'Due in 30 days'), set to null."
    )
    .compile()
)
```

### Missing Data

```python
prompt = (
    StructuredPrompt()
    .add_general_rule(
        "For missing or unclear values:",
        "- Use null for completely missing fields.",
        "- Use empty string '' for blank fields that exist.",
        "- NEVER invent data that isn't in the document."
    )
    .compile()
)
```

### Multi-Language Documents

```python
prompt = (
    StructuredPrompt()
    .add_general_rule(
        "Document may contain multiple languages.",
        "Extract names/companies in original language.",
        "Normalize dates to YYYY-MM-DD regardless of format."
    )
    .compile()
)
```

---

## Few-Shot Examples

Add examples for complex fields:

```python
prompt = (
    StructuredPrompt()
    .add_field_rule(
        "vendor_name",
        "Extract the vendor/seller company name.",
        "Examples:",
        "  - 'ACME Corp.' → 'ACME Corp.'",
        "  - 'From: Big Company LLC' → 'Big Company LLC'",
        "  - 'Invoice from ABC Inc.\\n123 Main St' → 'ABC Inc.'"
    )
    .compile()
)
```

---

## Combining with Schema Descriptions

Use Pydantic Field descriptions alongside StructuredPrompt:

```python
from pydantic import BaseModel, Field
from strutex.prompts import StructuredPrompt

class Invoice(BaseModel):
    invoice_number: str = Field(
        description="Unique invoice ID, starts with INV or #"
    )
    total: float = Field(
        description="Final amount after tax"
    )

prompt = (
    StructuredPrompt()
    .add_general_rule("Use ISO dates.", "No guessing.")
    .add_field_rule("total", "Verify math: subtotal + tax = total.", critical=True)
    .compile()
)

# Both prompt AND schema descriptions guide the LLM
result = processor.process("invoice.pdf", prompt, model=Invoice)
```

---

## Verification Prompts

Customize the self-correction pass:

```python
result = processor.process(
    file_path="invoice.pdf",
    prompt=INVOICE_PROMPT,
    model=Invoice,
    verify=True,
    verify_prompt="""
    Audit the extracted data against the document.

    Check:
    1. Do line item totals sum to subtotal?
    2. Does subtotal + tax = total?
    3. Are all visible line items captured?

    Correct any errors and return the fixed JSON.
    """
)
```

---

## Debugging Prompts

### See the Final Prompt

```python
prompt = StructuredPrompt()
prompt.add_general_rule("Rule 1", "Rule 2")
prompt.add_field_rule("total", "Must be numeric", critical=True)

# View the compiled prompt
print(prompt.compile())

# Or check structure
print(repr(prompt))
# StructuredPrompt(general_rules=2, field_rules=1, output_guidelines=0)
```

### A/B Test Prompts

```python
prompts = [
    StructuredPrompt().add_general_rule("Extract all data").compile(),
    StructuredPrompt().add_general_rule("Carefully extract all visible data").compile(),
]

for p in prompts:
    result = processor.process("test.pdf", p, model=Invoice)
    print(f"Prompt: {p[:50]}... → Total: {result.total}")
```

---

## Best Practices

| Practice                                   | Why                     |
| ------------------------------------------ | ----------------------- |
| Use `StructuredPrompt` for complex prompts | Clear organization      |
| Mark critical fields                       | LLM pays more attention |
| Specify date/number formats                | Consistent output       |
| Add examples for tricky fields             | Better accuracy         |
| Keep persona relevant                      | Sets context            |
| Use `verify=True` for critical data        | Catches mistakes        |

---

## Next Steps

| Want to...            | Go to...                                     |
| --------------------- | -------------------------------------------- |
| See complete examples | [Use Cases](tutorial-use-cases.md)           |
| Add validation        | [Validation](tutorial-validation.md)         |
| Handle errors         | [Error Handling](tutorial-error-handling.md) |
