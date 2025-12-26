"""
strutex.schemas - Ready-to-use Pydantic schemas for common documents.

Provides pre-built schemas for invoices, receipts, purchase orders, and more.
Use these directly with DocumentProcessor for instant structured extraction.

Example:
    >>> from strutex import DocumentProcessor
    >>> from strutex.schemas import INVOICE_US
    >>> 
    >>> processor = DocumentProcessor(provider="gemini")
    >>> result = processor.process("invoice.pdf", "Extract invoice", model=INVOICE_US)
    >>> print(result.invoice_number)

Available Schemas:
    - INVOICE_GENERIC, INVOICE_US, INVOICE_EU
    - RECEIPT
    - PURCHASE_ORDER
    - BILL_OF_LADING
    - BANK_STATEMENT
    - RESUME
    - CONTRACT_CLAUSE
"""

from .invoice import (
    InvoiceGeneric,
    InvoiceUS,
    InvoiceEU,
    INVOICE_GENERIC,
    INVOICE_US,
    INVOICE_EU,
)

from .receipt import (
    Receipt,
    RECEIPT,
)

from .purchase_order import (
    PurchaseOrder,
    PURCHASE_ORDER,
)

from .shipping import (
    BillOfLading,
    BILL_OF_LADING,
)

from .financial import (
    BankStatement,
    BankTransaction,
    BANK_STATEMENT,
)

from .resume import (
    Resume,
    RESUME,
)

from .legal import (
    ContractClause,
    CONTRACT_CLAUSE,
)

__all__ = [
    # Invoices
    "InvoiceGeneric",
    "InvoiceUS", 
    "InvoiceEU",
    "INVOICE_GENERIC",
    "INVOICE_US",
    "INVOICE_EU",
    
    # Receipts
    "Receipt",
    "RECEIPT",
    
    # Purchase Orders
    "PurchaseOrder",
    "PURCHASE_ORDER",
    
    # Shipping
    "BillOfLading",
    "BILL_OF_LADING",
    
    # Financial
    "BankStatement",
    "BankTransaction",
    "BANK_STATEMENT",
    
    # Resume/CV
    "Resume",
    "RESUME",
    
    # Legal
    "ContractClause",
    "CONTRACT_CLAUSE",
]
