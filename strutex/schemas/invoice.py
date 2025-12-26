"""
Invoice schemas for structured extraction.

Provides Pydantic models for different invoice formats (US, EU, generic).
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class Address(BaseModel):
    """Postal address."""
    street: Optional[str] = Field(None, description="Street address including unit/suite")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State, province, or region")
    postal_code: Optional[str] = Field(None, description="ZIP or postal code")
    country: Optional[str] = Field(None, description="Country name or code")


class Party(BaseModel):
    """A party in a transaction (vendor, customer, etc.)."""
    name: str = Field(..., description="Company or individual name")
    address: Optional[Address] = Field(None, description="Postal address")
    email: Optional[str] = Field(None, description="Email address")
    phone: Optional[str] = Field(None, description="Phone number")
    tax_id: Optional[str] = Field(None, description="Tax ID, VAT number, or EIN")


class InvoiceLineItem(BaseModel):
    """A single line item on an invoice."""
    description: str = Field(..., description="Description of the item or service")
    quantity: Optional[float] = Field(None, description="Quantity of items")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    amount: float = Field(..., description="Line total amount")
    sku: Optional[str] = Field(None, description="SKU or product code")
    unit: Optional[str] = Field(None, description="Unit of measure (ea, kg, hr, etc.)")


class InvoiceGeneric(BaseModel):
    """
    Generic invoice schema suitable for most invoice types.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import INVOICE_GENERIC
        >>> 
        >>> processor = DocumentProcessor()
        >>> invoice = processor.process("invoice.pdf", "Extract invoice", model=INVOICE_GENERIC)
        >>> print(f"Invoice {invoice.invoice_number}: ${invoice.total}")
    """
    
    # Identifiers
    invoice_number: str = Field(..., description="Invoice number or ID")
    invoice_date: Optional[str] = Field(None, description="Invoice date (YYYY-MM-DD preferred)")
    due_date: Optional[str] = Field(None, description="Payment due date")
    po_number: Optional[str] = Field(None, description="Purchase order reference")
    
    # Parties
    vendor: Optional[Party] = Field(None, description="Seller/vendor information")
    customer: Optional[Party] = Field(None, description="Buyer/customer/bill-to information")
    ship_to: Optional[Address] = Field(None, description="Shipping address if different from billing")
    
    # Financial
    currency: str = Field("USD", description="Currency code (USD, EUR, GBP, etc.)")
    subtotal: Optional[float] = Field(None, description="Subtotal before tax and discounts")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    tax_rate: Optional[float] = Field(None, description="Tax rate as percentage")
    discount: Optional[float] = Field(None, description="Discount amount")
    shipping: Optional[float] = Field(None, description="Shipping/freight charges")
    total: float = Field(..., description="Grand total amount due")
    amount_paid: Optional[float] = Field(None, description="Amount already paid")
    balance_due: Optional[float] = Field(None, description="Remaining balance")
    
    # Line items
    line_items: List[InvoiceLineItem] = Field(
        default_factory=list,
        description="List of line items on the invoice"
    )
    
    # Payment
    payment_terms: Optional[str] = Field(None, description="Payment terms (Net 30, Due on receipt, etc.)")
    payment_method: Optional[str] = Field(None, description="Payment method or instructions")
    bank_details: Optional[str] = Field(None, description="Bank account details for wire transfer")
    
    # Notes
    notes: Optional[str] = Field(None, description="Additional notes or comments")


class InvoiceUS(InvoiceGeneric):
    """
    US-style invoice with additional US-specific fields.
    
    Includes fields for:
    - Sales tax breakdown by state
    - EIN/Tax ID formatting
    - US address format
    """
    
    # US-specific
    sales_tax: Optional[float] = Field(None, description="State/local sales tax")
    state_tax_rate: Optional[float] = Field(None, description="State tax rate percentage")
    ein: Optional[str] = Field(None, description="Employer Identification Number")


class InvoiceEU(InvoiceGeneric):
    """
    EU-style invoice with VAT support.
    
    Includes fields for:
    - VAT number and rates
    - Intra-community supplies
    - Reverse charge mechanism
    """
    
    # EU/VAT-specific
    vat_number: Optional[str] = Field(None, description="VAT registration number")
    vat_rate: Optional[float] = Field(None, description="VAT rate percentage")
    vat_amount: Optional[float] = Field(None, description="VAT amount")
    net_amount: Optional[float] = Field(None, description="Amount excluding VAT")
    gross_amount: Optional[float] = Field(None, description="Amount including VAT")
    reverse_charge: bool = Field(False, description="Whether reverse charge applies")
    intra_community: bool = Field(False, description="Intra-community supply (0% VAT)")


# Convenient schema instances for direct use
INVOICE_GENERIC = InvoiceGeneric
INVOICE_US = InvoiceUS
INVOICE_EU = InvoiceEU
