from typing import List, Dict, Any
import asyncio
from pdf_extractor import PDFExtractor
from classifier import DocumentClassifier
from agents import BillAgent, DischargeAgent, IDAgent, PharmacyAgent, ClaimFormAgent
from validator import ClaimValidator
from decision_maker import DecisionMaker
from models import Document, DocumentType

class ClaimOrchestrator:
    def __init__(self):
        self.pdf_extractor = PDFExtractor()
        self.classifier = DocumentClassifier()
        self.validator = ClaimValidator()
        self.decision_maker = DecisionMaker()
        
        self.agents = {
            DocumentType.BILL: BillAgent(),
            DocumentType.DISCHARGE_SUMMARY: DischargeAgent(),
            DocumentType.ID_CARD: IDAgent(),
            DocumentType.PHARMACY_BILL: PharmacyAgent(),
            DocumentType.CLAIM_FORM: ClaimFormAgent()
        }
    
    async def process_claim(self, pdf_files: List[Dict[str, Any]]) -> Dict[str, Any]:
        documents = await self._process_documents(pdf_files)
        
        validation = await self.validator.validate(documents)
        
        decision = await self.decision_maker.make_decision(documents, validation)
        
        return {
            "documents": [doc.dict() for doc in documents],
            "validation": validation.dict(),
            "claim_decision": decision.dict()
        }
    
    async def _process_documents(self, pdf_files: List[Dict[str, Any]]) -> List[Document]:
        tasks = [self._process_single_document(pdf_file) for pdf_file in pdf_files]
        documents = await asyncio.gather(*tasks)
        return documents
    
    async def _process_single_document(self, pdf_file: Dict[str, Any]) -> Document:
        filename = pdf_file["filename"]
        content = pdf_file["content"]
        
        text = await self.pdf_extractor.extract_text(content)
        
        doc_type = await self.classifier.classify(text, filename)
        
        agent = self.agents.get(doc_type)
        
        if agent:
            extracted_data = await agent.extract(text)
        else:
            extracted_data = {
                "raw_text": text[:500],
                "note": "No specific agent for this document type"
            }
        
        return Document(
            filename=filename,
            document_type=doc_type,
            extracted_data=extracted_data
        )
