from typing import Dict, Any
from agents.base_agent import BaseAgent

class ClaimFormAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from insurance claim forms.
Extract all claim-related information accurately."""
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Extract structured data from this insurance claim form.

Document text:
{text}

Return ONLY valid JSON with these fields:
{{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "claim_number": "string or null",
    "claim_date": "YYYY-MM-DD or null",
    "insurance_company": "string or null",
    "policy_number": "string or null",
    "claimed_amount": "float or null",
    "diagnosis": "string or null",
    "treatment_date": "YYYY-MM-DD or null",
    "provider_name": "string or null"
}}

Use null for any field you cannot extract."""
