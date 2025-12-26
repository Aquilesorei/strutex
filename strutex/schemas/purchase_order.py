"""
Purchase Order schema for structured extraction.

Covers standard B2B purchase orders with items, delivery, and payment terms.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class POLineItem(BaseModel):
    """A single line item on a purchase order."""
    line_number: Optional[int] = Field(None, description="Line item number")
    part_number: Optional[str] = Field(None, description="Part/SKU number")
    description: str = Field(..., description="Item description")
    quantity: float = Field(..., description="Quantity ordered")
    unit: Optional[str] = Field(None, description="Unit of measure")
    unit_price: float = Field(..., description="Unit price")
    amount: float = Field(..., description="Line total (qty × price)")
    delivery_date: Optional[str] = Field(None, description="Requested delivery date")


class POAddress(BaseModel):
    """Address for purchase order."""
    company: Optional[str] = Field(None, description="Company name")
    attention: Optional[str] = Field(None, description="Attention/contact person")
    street: Optional[str] = Field(None, description="Street address")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/province")
    postal_code: Optional[str] = Field(None, description="ZIP/postal code")
    country: Optional[str] = Field(None, description="Country")


class PurchaseOrder(BaseModel):
    """
    Standard purchase order schema for B2B transactions.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import PURCHASE_ORDER
        >>> 
        >>> processor = DocumentProcessor()
        >>> po = processor.process("po.pdf", "Extract PO", model=PURCHASE_ORDER)
        >>> print(f"PO #{po.po_number}: {len(po.line_items)} items, ${po.total}")
    """
    
    # PO identification
    po_number: str = Field(..., description="Purchase order number")
    po_date: Optional[str] = Field(None, description="PO issue date")
    revision: Optional[str] = Field(None, description="Revision number")
    
    # References
    quote_number: Optional[str] = Field(None, description="Reference quote number")
    contract_number: Optional[str] = Field(None, description="Contract/agreement number")
    requisition_number: Optional[str] = Field(None, description="Internal requisition number")
    
    # Parties
    buyer_name: Optional[str] = Field(None, description="Buying company name")
    buyer_contact: Optional[str] = Field(None, description="Buyer contact person")
    buyer_email: Optional[str] = Field(None, description="Buyer email")
    buyer_phone: Optional[str] = Field(None, description="Buyer phone")
    
    vendor_name: str = Field(..., description="Vendor/supplier name")
    vendor_code: Optional[str] = Field(None, description="Vendor code in buyer's system")
    vendor_contact: Optional[str] = Field(None, description="Vendor contact person")
    
    # Addresses
    ship_to: Optional[POAddress] = Field(None, description="Ship-to address")
    bill_to: Optional[POAddress] = Field(None, description="Bill-to address")
    
    # Line items
    line_items: List[POLineItem] = Field(
        default_factory=list,
        description="Ordered items"
    )
    
    # Totals
    currency: str = Field("USD", description="Currency code")
    subtotal: Optional[float] = Field(None, description="Subtotal before tax/shipping")
    tax: Optional[float] = Field(None, description="Tax amount")
    shipping: Optional[float] = Field(None, description="Shipping/freight cost")
    total: float = Field(..., description="Total PO value")
    
    # Terms
    payment_terms: Optional[str] = Field(None, description="Payment terms (Net 30, etc.)")
    delivery_terms: Optional[str] = Field(None, description="Delivery/shipping terms (FOB, CIF, etc.)")
    required_date: Optional[str] = Field(None, description="Required delivery date")
    
    # Notes
    notes: Optional[str] = Field(None, description="Special instructions or notes")


# Convenient schema instance
PURCHASE_ORDER = PurchaseOrder
