"""
Financial document schemas for structured extraction.

Covers bank statements and transaction records.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class BankTransaction(BaseModel):
    """A single bank transaction."""
    date: str = Field(..., description="Transaction date (YYYY-MM-DD)")
    description: str = Field(..., description="Transaction description")
    reference: Optional[str] = Field(None, description="Reference/check number")
    debit: Optional[float] = Field(None, description="Debit/withdrawal amount")
    credit: Optional[float] = Field(None, description="Credit/deposit amount")
    balance: Optional[float] = Field(None, description="Running balance after transaction")
    category: Optional[str] = Field(None, description="Transaction category")
    type: Optional[str] = Field(None, description="Transaction type (ATM, Transfer, POS, etc.)")


class BankStatement(BaseModel):
    """
    Bank statement schema for account statements.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import BANK_STATEMENT
        >>> 
        >>> processor = DocumentProcessor()
        >>> stmt = processor.process("statement.pdf", "Extract statement", model=BANK_STATEMENT)
        >>> print(f"Account {stmt.account_number}: {len(stmt.transactions)} transactions")
    """
    
    # Bank info
    bank_name: str = Field(..., description="Bank/institution name")
    bank_address: Optional[str] = Field(None, description="Bank branch address")
    
    # Account info
    account_holder: str = Field(..., description="Account holder name")
    account_number: str = Field(..., description="Account number (may be masked)")
    account_type: Optional[str] = Field(None, description="Account type (Checking, Savings, etc.)")
    
    # Statement period
    statement_date: Optional[str] = Field(None, description="Statement date")
    period_start: Optional[str] = Field(None, description="Period start date")
    period_end: Optional[str] = Field(None, description="Period end date")
    
    # Balances
    opening_balance: float = Field(..., description="Beginning balance")
    closing_balance: float = Field(..., description="Ending balance")
    
    # Summary
    total_deposits: Optional[float] = Field(None, description="Total credits/deposits")
    total_withdrawals: Optional[float] = Field(None, description="Total debits/withdrawals")
    total_fees: Optional[float] = Field(None, description="Total fees charged")
    interest_earned: Optional[float] = Field(None, description="Interest earned")
    
    # Transactions
    transactions: List[BankTransaction] = Field(
        default_factory=list,
        description="List of transactions"
    )
    
    # Currency
    currency: str = Field("USD", description="Account currency")


# Convenient schema instances
BANK_STATEMENT = BankStatement
