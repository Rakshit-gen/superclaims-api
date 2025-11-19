from llm_client import LLMClient
from models import DocumentType

class DocumentClassifier:
    def __init__(self):
        self.llm_client = LLMClient()
    
    async def classify(self, text: str, filename: str) -> DocumentType:
        system_prompt = """You are a document classification expert for medical claims. 
Classify documents accurately based on their content."""

        prompt = f"""Classify this medical document into ONE of these categories:
- bill: Medical bills, hospital invoices
- discharge_summary: Patient discharge summaries, medical reports
- id_card: Insurance ID cards, patient identification
- pharmacy_bill: Pharmacy receipts, prescription bills
- claim_form: Insurance claim forms
- other: Any other document type

Document filename: {filename}

Document content:
{text[:2000]}

Respond with ONLY a JSON object in this exact format:
{{"document_type": "bill|discharge_summary|id_card|pharmacy_bill|claim_form|other", "confidence": 0.95, "reasoning": "brief explanation"}}"""

        result = await self.llm_client.generate_json(prompt, system_prompt)
        
        doc_type = result.get("document_type", "other")
        
        try:
            return DocumentType(doc_type)
        except ValueError:
            return DocumentType.OTHER
