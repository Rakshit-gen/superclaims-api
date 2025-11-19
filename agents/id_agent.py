from typing import Dict, Any
from agents.base_agent import BaseAgent

class IDAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from insurance ID cards and patient identification documents.
Extract all identification information accurately."""
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Extract structured data from this insurance ID card or patient identification document.

Document text:
{text}

Return ONLY valid JSON with these fields:
{{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "insurance_company": "string or null",
    "policy_number": "string or null",
    "group_number": "string or null",
    "date_of_birth": "YYYY-MM-DD or null",
    "valid_from": "YYYY-MM-DD or null",
    "valid_until": "YYYY-MM-DD or null",
    "member_id": "string or null"
}}

Use null for any field you cannot extract."""
