"""
Receipt schema for structured extraction.

Covers retail receipts, restaurant checks, and general point-of-sale receipts.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ReceiptItem(BaseModel):
    """A single item on a receipt."""
    description: str = Field(..., description="Item name or description")
    quantity: Optional[float] = Field(1.0, description="Quantity purchased")
    unit_price: Optional[float] = Field(None, description="Price per unit")
    amount: float = Field(..., description="Line total")
    sku: Optional[str] = Field(None, description="SKU or product code")
    category: Optional[str] = Field(None, description="Product category")


class Receipt(BaseModel):
    """
    General receipt schema for retail/restaurant transactions.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import RECEIPT
        >>> 
        >>> processor = DocumentProcessor()
        >>> receipt = processor.process("receipt.jpg", "Extract receipt", model=RECEIPT)
        >>> print(f"Store: {receipt.merchant_name}, Total: ${receipt.total}")
    """
    
    # Merchant info
    merchant_name: str = Field(..., description="Store or merchant name")
    merchant_address: Optional[str] = Field(None, description="Store address")
    merchant_phone: Optional[str] = Field(None, description="Store phone number")
    store_number: Optional[str] = Field(None, description="Store/location number")
    
    # Transaction info
    receipt_number: Optional[str] = Field(None, description="Receipt or transaction number")
    date: Optional[str] = Field(None, description="Transaction date (YYYY-MM-DD)")
    time: Optional[str] = Field(None, description="Transaction time (HH:MM)")
    cashier: Optional[str] = Field(None, description="Cashier name or ID")
    register_number: Optional[str] = Field(None, description="Register or terminal number")
    
    # Items
    items: List[ReceiptItem] = Field(
        default_factory=list,
        description="List of purchased items"
    )
    
    # Totals
    subtotal: Optional[float] = Field(None, description="Subtotal before tax")
    tax: Optional[float] = Field(None, description="Tax amount")
    tax_rate: Optional[float] = Field(None, description="Tax rate percentage")
    tip: Optional[float] = Field(None, description="Tip/gratuity (for restaurants)")
    discount: Optional[float] = Field(None, description="Discount amount")
    total: float = Field(..., description="Total amount paid")
    
    # Payment
    payment_method: Optional[str] = Field(None, description="Payment method (Cash, Card, etc.)")
    card_last_four: Optional[str] = Field(None, description="Last 4 digits of card")
    amount_tendered: Optional[float] = Field(None, description="Amount given/tendered")
    change: Optional[float] = Field(None, description="Change given")
    
    # Rewards/loyalty
    loyalty_number: Optional[str] = Field(None, description="Loyalty/rewards card number")
    points_earned: Optional[int] = Field(None, description="Loyalty points earned")


# Convenient schema instance
RECEIPT = Receipt
