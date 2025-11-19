from typing import Dict, Any
from agents.base_agent import BaseAgent

class DischargeAgent(BaseAgent):
    def get_system_prompt(self) -> str:
        return """You are an expert at extracting structured data from hospital discharge summaries.
Extract all relevant medical and patient information accurately."""
    
    def get_extraction_prompt(self, text: str) -> str:
        return f"""Extract structured data from this discharge summary.

Document text:
{text}

Return ONLY valid JSON with these fields:
{{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "admission_date": "YYYY-MM-DD or null",
    "discharge_date": "YYYY-MM-DD or null",
    "diagnosis": "string or null",
    "procedures": ["list of procedures or empty array"],
    "medications": ["list of medications or empty array"],
    "doctor_name": "string or null",
    "hospital_name": "string or null",
    "follow_up_required": "boolean or null"
}}

Use null for any field you cannot extract."""
