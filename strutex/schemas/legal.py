"""
Legal document schemas for structured extraction.

Covers contract clauses and legal document excerpts.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class ContractParty(BaseModel):
    """A party to a contract."""
    name: str = Field(..., description="Party name (individual or entity)")
    role: Optional[str] = Field(None, description="Role in contract (Buyer, Seller, Licensor, etc.)")
    address: Optional[str] = Field(None, description="Address")
    representative: Optional[str] = Field(None, description="Authorized representative")


class ContractClause(BaseModel):
    """
    Contract clause/section schema for legal document extraction.
    
    Example:
        >>> from strutex import DocumentProcessor
        >>> from strutex.schemas import CONTRACT_CLAUSE
        >>> 
        >>> processor = DocumentProcessor()
        >>> clause = processor.process(
        ...     "contract.pdf",
        ...     "Extract key contract terms",
        ...     model=CONTRACT_CLAUSE
        ... )
        >>> print(f"Contract: {clause.title}, Effective: {clause.effective_date}")
    """
    
    # Document identification
    title: Optional[str] = Field(None, description="Contract/agreement title")
    contract_type: Optional[str] = Field(None, description="Type (NDA, MSA, SLA, etc.)")
    contract_number: Optional[str] = Field(None, description="Contract ID/number")
    
    # Parties
    parties: List[ContractParty] = Field(
        default_factory=list,
        description="Parties to the contract"
    )
    
    # Dates
    effective_date: Optional[str] = Field(None, description="Effective/start date")
    expiration_date: Optional[str] = Field(None, description="Expiration/end date")
    execution_date: Optional[str] = Field(None, description="Signing/execution date")
    
    # Key terms
    term_length: Optional[str] = Field(None, description="Contract term/duration")
    renewal_terms: Optional[str] = Field(None, description="Auto-renewal provisions")
    termination_clause: Optional[str] = Field(None, description="Termination conditions")
    
    # Financial
    total_value: Optional[float] = Field(None, description="Total contract value")
    payment_terms: Optional[str] = Field(None, description="Payment terms and schedule")
    currency: Optional[str] = Field(None, description="Contract currency")
    
    # Legal
    governing_law: Optional[str] = Field(None, description="Governing law/jurisdiction")
    dispute_resolution: Optional[str] = Field(None, description="Dispute resolution mechanism")
    confidentiality: Optional[str] = Field(None, description="Confidentiality provisions")
    indemnification: Optional[str] = Field(None, description="Indemnification clause summary")
    limitation_of_liability: Optional[str] = Field(None, description="Liability limitations")
    
    # Specific clauses (extracted text)
    key_obligations: List[str] = Field(
        default_factory=list,
        description="Key obligations of parties"
    )
    
    warranties: List[str] = Field(
        default_factory=list,
        description="Warranties and representations"
    )
    
    # Signatures
    signed_by: List[str] = Field(
        default_factory=list,
        description="Names of signatories"
    )


# Convenient schema instance
CONTRACT_CLAUSE = ContractClause
