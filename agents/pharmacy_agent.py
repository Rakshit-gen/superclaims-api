from typing import Dict, Any
from agents.base_agent import BaseAgent

class PharmacyAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from pharmacy bills and prescription receipts.
Extract all relevant medication and pricing information accurately."""
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Extract structured data from this pharmacy bill.

Document text:
{text}

Return ONLY valid JSON with these fields:
{{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "pharmacy_name": "string or null",
    "bill_date": "YYYY-MM-DD or null",
    "prescription_number": "string or null",
    "medications": [
        {{
            "name": "string",
            "quantity": "string",
            "price": "float"
        }}
    ],
    "total_amount": "float or null",
    "doctor_name": "string or null"
}}

Use null for any field you cannot extract."""
