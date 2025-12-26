#!/usr/bin/env python3
"""
Example: Using Built-in Schemas

This example demonstrates how to use strutex's built-in Pydantic
schemas for common document types like invoices, receipts, and more.
"""

from strutex.schemas import (
    # Invoice schemas
    INVOICE_GENERIC,
    INVOICE_US,
    INVOICE_EU,
    InvoiceGeneric,
    InvoiceUS,
    InvoiceEU,
    
    # Other schemas
    RECEIPT,
    PURCHASE_ORDER,
    BILL_OF_LADING,
    BANK_STATEMENT,
    RESUME,
    CONTRACT_CLAUSE,
    
    # Classes for customization
    Receipt,
    PurchaseOrder,
    BillOfLading,
    BankStatement,
    Resume,
    ContractClause,
)


def example_quick_usage():
    """Using pre-configured schema instances."""
    print("=" * 60)
    print("Example 1: Quick Usage with Schema Instances")
    print("=" * 60)
    
    print("""
    from strutex import DocumentProcessor
    from strutex.schemas import INVOICE_US
    
    processor = DocumentProcessor(provider="gemini")
    
    # Use INVOICE_US (a pre-configured instance)
    result = processor.process(
        file_path="invoice.pdf",
        prompt="Extract all invoice details",
        model=INVOICE_US
    )
    
    print(f"Invoice #: {result.invoice_number}")
    print(f"Total: ${result.total}")
    print(f"Vendor: {result.vendor.name if result.vendor else 'N/A'}")
    """)


def example_available_schemas():
    """List all available schema types."""
    print("\n" + "=" * 60)
    print("Example 2: Available Schema Types")
    print("=" * 60)
    
    schemas = {
        "INVOICE_GENERIC": INVOICE_GENERIC,
        "INVOICE_US": INVOICE_US,
        "INVOICE_EU": INVOICE_EU,
        "RECEIPT": RECEIPT,
        "PURCHASE_ORDER": PURCHASE_ORDER,
        "BILL_OF_LADING": BILL_OF_LADING,
        "BANK_STATEMENT": BANK_STATEMENT,
        "RESUME": RESUME,
        "CONTRACT_CLAUSE": CONTRACT_CLAUSE,
    }
    
    for name, schema in schemas.items():
        fields = list(schema.model_fields.keys())
        print(f"\n{name}:")
        print(f"  Fields ({len(fields)}): {', '.join(fields[:5])}...")


def example_invoice_fields():
    """Explore invoice schema fields."""
    print("\n" + "=" * 60)
    print("Example 3: Invoice Schema Fields")
    print("=" * 60)
    
    # InvoiceGeneric fields
    print("\nInvoiceGeneric fields:")
    for name, field in InvoiceGeneric.model_fields.items():
        print(f"  {name}: {field.annotation}")
    
    # US-specific additions
    print("\nInvoiceUS additional fields:")
    us_only = set(InvoiceUS.model_fields.keys()) - set(InvoiceGeneric.model_fields.keys())
    for name in us_only:
        field = InvoiceUS.model_fields[name]
        print(f"  {name}: {field.annotation}")
    
    # EU-specific additions
    print("\nInvoiceEU additional fields:")
    eu_only = set(InvoiceEU.model_fields.keys()) - set(InvoiceGeneric.model_fields.keys())
    for name in eu_only:
        field = InvoiceEU.model_fields[name]
        print(f"  {name}: {field.annotation}")


def example_receipt_processing():
    """Using Receipt schema."""
    print("\n" + "=" * 60)
    print("Example 4: Receipt Processing")
    print("=" * 60)
    
    print("""
    from strutex import DocumentProcessor
    from strutex.schemas import RECEIPT
    
    processor = DocumentProcessor(provider="gemini")
    
    result = processor.process(
        file_path="receipt.jpg",
        prompt="Extract receipt details",
        model=RECEIPT
    )
    
    print(f"Merchant: {result.merchant_name}")
    print(f"Date: {result.date}")
    print(f"Total: ${result.total}")
    print(f"Payment: {result.payment_method}")
    
    # Items
    for item in result.items:
        print(f"  - {item.description}: ${item.unit_price} x {item.quantity}")
    """)


def example_custom_schema():
    """Extending built-in schemas."""
    print("\n" + "=" * 60)
    print("Example 5: Extending Schemas")
    print("=" * 60)
    
    from pydantic import Field
    from typing import Optional
    
    # Create a custom invoice with additional fields
    class CustomInvoice(InvoiceUS):
        """US Invoice with custom fields."""
        
        # Add custom fields
        internal_reference: Optional[str] = Field(
            None, description="Internal tracking number"
        )
        approved_by: Optional[str] = Field(
            None, description="Approver name"
        )
        cost_center: Optional[str] = Field(
            None, description="Cost center code"
        )
    
    print("CustomInvoice fields:")
    custom_fields = set(CustomInvoice.model_fields.keys()) - set(InvoiceUS.model_fields.keys())
    for name in custom_fields:
        print(f"  {name}")
    
    print("\nUsage:")
    print("""
    result = processor.process(
        file_path="invoice.pdf",
        prompt="Extract invoice with internal reference",
        model=CustomInvoice
    )
    
    print(f"Internal ref: {result.internal_reference}")
    print(f"Approved by: {result.approved_by}")
    """)


def example_bill_of_lading():
    """Using Bill of Lading schema for shipping."""
    print("\n" + "=" * 60)
    print("Example 6: Bill of Lading (Shipping)")
    print("=" * 60)
    
    print("BillOfLading fields:")
    for name, field in BillOfLading.model_fields.items():
        desc = field.description or ""
        print(f"  {name}: {desc[:50]}")


def example_bank_statement():
    """Using Bank Statement schema."""
    print("\n" + "=" * 60)
    print("Example 7: Bank Statement")
    print("=" * 60)
    
    print("BankStatement fields:")
    for name, field in BankStatement.model_fields.items():
        desc = field.description or ""
        print(f"  {name}: {desc[:50]}")


if __name__ == "__main__":
    example_quick_usage()
    example_available_schemas()
    example_invoice_fields()
    example_receipt_processing()
    example_custom_schema()
    example_bill_of_lading()
    example_bank_statement()
    
    print("\n" + "=" * 60)
    print("Built-in Schemas Examples Complete!")
    print("=" * 60)
