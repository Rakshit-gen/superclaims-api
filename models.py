from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from enum import Enum

class DocumentType(str, Enum):
    BILL = "bill"
    DISCHARGE_SUMMARY = "discharge_summary"
    ID_CARD = "id_card"
    PHARMACY_BILL = "pharmacy_bill"
    CLAIM_FORM = "claim_form"
    OTHER = "other"

class ClaimStatus(str, Enum):
    APPROVED = "approved"
    REJECTED = "rejected"
    MANUAL_REVIEW = "manual_review"

class Document(BaseModel):
    filename: str
    document_type: DocumentType
    extracted_data: Dict[str, Any]
    confidence: Optional[float] = None

class ValidationResult(BaseModel):
    missing_documents: List[str]
    discrepancies: List[Dict[str, Any]]

class ClaimDecision(BaseModel):
    status: ClaimStatus
    reason: str
    confidence: Optional[float] = None

class ClaimResponse(BaseModel):
    documents: List[Document]
    validation: ValidationResult
    claim_decision: ClaimDecision
