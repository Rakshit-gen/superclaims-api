from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import asyncio
from orchestrator import ClaimOrchestrator
from models import ClaimResponse

app = FastAPI(title="SuperClaims API", version="1.0.0")

orchestrator = ClaimOrchestrator()

@app.get("/")
async def root():
    return {"message": "SuperClaims API", "status": "running"}

@app.post("/process-claim", response_model=ClaimResponse)
async def process_claim(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided")
    
    try:
        pdf_files = []
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            content = await file.read()
            pdf_files.append({
                "filename": file.filename,
                "content": content
            })
        
        result = await orchestrator.process_claim(pdf_files)
        return JSONResponse(content=result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
