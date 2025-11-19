from abc import ABC, abstractmethod
from typing import Dict, Any
from llm_client import LLMClient

class BaseAgent(ABC):
    def __init__(self):
        self.llm_client = LLMClient()
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        pass
    
    @abstractmethod
    def get_extraction_prompt(self, text: str) -> str:
        pass
    
    async def extract(self, text: str) -> Dict[str, Any]:
        system_prompt = self.get_system_prompt()
        user_prompt = self.get_extraction_prompt(text)
        
        result = await self.llm_client.generate_json(user_prompt, system_prompt)
        return result
