from typing import Dict, Any
from agents.base_agent import BaseAgent

class BillAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from medical bills and invoices.
Extract all relevant information accurately. Use null for missing values."""
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Extract structured data from this medical bill.

Document text:
{text}

Return ONLY valid JSON with these fields:
{{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "bill_number": "string or null",
    "bill_date": "YYYY-MM-DD or null",
    "hospital_name": "string or null",
    "total_amount": "float or null",
    "items": [
        {{
            "description": "string",
            "amount": "float"
        }}
    ],
    "payment_status": "paid|pending|partial or null"
}}

Use null for any field you cannot extract."""
