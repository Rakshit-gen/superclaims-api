from typing import List, Dict, Any
from models import Document, ValidationResult, ClaimDecision, ClaimStatus
from llm_client import LLMClient
import json

class DecisionMaker:
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def make_decision(
        self, 
        documents: List[Document], 
        validation: ValidationResult
    ) -> ClaimDecision:
        if validation.missing_documents:
            return ClaimDecision(
                status=ClaimStatus.REJECTED,
                reason=f"Missing required documents: {', '.join(validation.missing_documents)}",
                confidence=1.0
            )
        
        if validation.discrepancies:
            critical_discrepancies = self._check_critical_discrepancies(validation.discrepancies)
            
            if critical_discrepancies:
                return ClaimDecision(
                    status=ClaimStatus.REJECTED,
                    reason=f"Critical discrepancies found: {critical_discrepancies[0]['description']}",
                    confidence=0.95
                )
            
            return ClaimDecision(
                status=ClaimStatus.MANUAL_REVIEW,
                reason=f"Minor discrepancies require manual review: {validation.discrepancies[0]['description']}",
                confidence=0.85
            )
        
        llm_decision = await self._llm_final_check(documents)
        
        return llm_decision
    
    def _check_critical_discrepancies(self, discrepancies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        critical_types = ["name_mismatch", "id_mismatch", "date_sequence_error"]
        return [d for d in discrepancies if d.get("type") in critical_types]
    
    async def _llm_final_check(self, documents: List[Document]) -> ClaimDecision:
        system_prompt = """You are a medical claims adjudication expert.
Review all documents and make a final claim decision."""

        docs_summary = []
        for doc in documents:
            docs_summary.append({
                "type": doc.document_type.value,
                "data": doc.extracted_data
            })
        
        prompt = f"""Review this medical claim and make a final decision.

Documents:
{json.dumps(docs_summary, indent=2)}

Consider:
1. Are all necessary documents present and complete?
2. Is the information consistent and reasonable?
3. Are there any red flags or suspicious patterns?
4. Is the claim amount reasonable for the treatment?

Respond with ONLY valid JSON:
{{
    "status": "approved|rejected|manual_review",
    "reason": "detailed explanation of the decision",
    "confidence": 0.0-1.0
}}"""

        result = await self.llm_client.generate_json(prompt, system_prompt)
        
        status_str = result.get("status", "manual_review")
        
        try:
            status = ClaimStatus(status_str)
        except ValueError:
            status = ClaimStatus.MANUAL_REVIEW
        
        return ClaimDecision(
            status=status,
            reason=result.get("reason", "LLM decision"),
            confidence=result.get("confidence", 0.8)
        )
