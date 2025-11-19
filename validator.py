from typing import List, Dict, Any
from models import Document, ValidationResult, DocumentType

class ClaimValidator:
    def __init__(self):
        self.required_documents = [
            DocumentType.BILL,
            DocumentType.ID_CARD,
            DocumentType.DISCHARGE_SUMMARY
        ]
    
    async def validate(self, documents: List[Document]) -> ValidationResult:
        missing_docs = await self._check_missing_documents(documents)
        discrepancies = await self._check_discrepancies(documents)
        
        return ValidationResult(
            missing_documents=missing_docs,
            discrepancies=discrepancies
        )
    
    async def _check_missing_documents(self, documents: List[Document]) -> List[str]:
        missing = []
        doc_types = {doc.document_type for doc in documents}
        
        for required_type in self.required_documents:
            if required_type not in doc_types:
                missing.append(required_type.value)
        
        return missing
    
    async def _check_discrepancies(self, documents: List[Document]) -> List[Dict[str, Any]]:
        discrepancies = []
        
        patient_names = self._extract_field(documents, "patient_name")
        if len(set(patient_names)) > 1:
            discrepancies.append({
                "type": "name_mismatch",
                "description": "Patient names do not match across documents",
                "values": list(set(patient_names))
            })
        
        patient_ids = self._extract_field(documents, "patient_id")
        if len(set(patient_ids)) > 1:
            discrepancies.append({
                "type": "id_mismatch",
                "description": "Patient IDs do not match across documents",
                "values": list(set(patient_ids))
            })
        
        dates = self._extract_dates(documents)
        date_issues = self._validate_date_sequence(dates)
        if date_issues:
            discrepancies.extend(date_issues)
        
        amounts = self._check_amount_consistency(documents)
        if amounts:
            discrepancies.extend(amounts)
        
        return discrepancies
    
    def _extract_field(self, documents: List[Document], field: str) -> List[str]:
        values = []
        for doc in documents:
            value = doc.extracted_data.get(field)
            if value and value != "null" and value is not None:
                values.append(str(value).strip().lower())
        return [v for v in values if v]
    
    def _extract_dates(self, documents: List[Document]) -> Dict[str, List[str]]:
        dates = {
            "admission": [],
            "discharge": [],
            "bill": [],
            "treatment": []
        }
        
        for doc in documents:
            data = doc.extracted_data
            
            if doc.document_type == DocumentType.DISCHARGE_SUMMARY:
                if data.get("admission_date"):
                    dates["admission"].append(data["admission_date"])
                if data.get("discharge_date"):
                    dates["discharge"].append(data["discharge_date"])
            
            elif doc.document_type == DocumentType.BILL:
                if data.get("bill_date"):
                    dates["bill"].append(data["bill_date"])
            
            elif doc.document_type == DocumentType.CLAIM_FORM:
                if data.get("treatment_date"):
                    dates["treatment"].append(data["treatment_date"])
        
        return dates
    
    def _validate_date_sequence(self, dates: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        issues = []
        
        if dates["admission"] and dates["discharge"]:
            admission = dates["admission"][0]
            discharge = dates["discharge"][0]
            
            if admission > discharge:
                issues.append({
                    "type": "date_sequence_error",
                    "description": "Admission date is after discharge date",
                    "admission_date": admission,
                    "discharge_date": discharge
                })
        
        return issues
    
    def _check_amount_consistency(self, documents: List[Document]) -> List[Dict[str, Any]]:
        issues = []
        
        bill_amounts = []
        claimed_amounts = []
        
        for doc in documents:
            data = doc.extracted_data
            
            if doc.document_type == DocumentType.BILL:
                if data.get("total_amount"):
                    bill_amounts.append(float(data["total_amount"]))
            
            if doc.document_type == DocumentType.CLAIM_FORM:
                if data.get("claimed_amount"):
                    claimed_amounts.append(float(data["claimed_amount"]))
        
        if bill_amounts and claimed_amounts:
            total_bill = sum(bill_amounts)
            total_claimed = sum(claimed_amounts)
            
            if abs(total_bill - total_claimed) > 0.01:
                issues.append({
                    "type": "amount_mismatch",
                    "description": "Claimed amount does not match total bill amount",
                    "total_bill_amount": total_bill,
                    "total_claimed_amount": total_claimed
                })
        
        return issues
