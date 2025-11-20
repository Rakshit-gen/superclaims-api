# SuperClaims Backend

A FastAPI-based medical claims processing system that uses LLM-powered agents to classify, extract, validate, and make decisions on medical claim documents.

## Architecture

### System Overview

```
PDF Upload → Classification → Text Extraction → Agent Processing → Validation → Decision
```

### Components

1. **FastAPI Application** (`main.py`)
   - REST API endpoint for claim processing
   - Async request handling
   - File upload management

2. **Orchestrator** (`orchestrator.py`)
   - Coordinates the entire processing pipeline
   - Manages parallel document processing
   - Aggregates results from multiple agents

3. **Document Classifier** (`classifier.py`)
   - Uses LLM to classify documents into types
   - Supported types: bill, discharge_summary, id_card, pharmacy_bill, claim_form, other

4. **Specialized Agents** (`agents/`)
   - **BillAgent**: Extracts data from medical bills
   - **DischargeAgent**: Processes discharge summaries
   - **IDAgent**: Extracts insurance ID information
   - **PharmacyAgent**: Processes pharmacy bills
   - **ClaimFormAgent**: Extracts claim form data

5. **Validator** (`validator.py`)
   - Checks for missing required documents
   - Cross-validates data consistency (names, IDs, dates, amounts)
   - Detects discrepancies across documents

6. **Decision Maker** (`decision_maker.py`)
   - Makes final claim decisions based on validation results
   - Uses LLM for complex decision scenarios
   - Returns: approved, rejected, or manual_review

### Data Flow

```
1. Client uploads multiple PDFs via POST /process-claim
2. Each PDF is extracted in parallel
3. PDFs are classified by document type
4. Type-specific agents extract structured data
5. Validator checks for completeness and consistency
6. Decision maker produces final verdict
7. JSON response returned to client
```

## Setup

### Prerequisites

- Python 3.10+
- GROQ API key

### Installation

```bash
git clone <repository-url>
cd superclaims-backend

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```
GROQ_API_KEY=...
LLM_MODEL=llama-3.3-70b-versatile
```

### Running the Server

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### Using Docker

```bash
docker-compose up --build
```

## API Usage

### Endpoint: POST /process-claim

**Request:**
```bash
curl -X POST "http://localhost:8000/process-claim" \
  -F "files=@medical_bill.pdf" \
  -F "files=@discharge_summary.pdf" \
  -F "files=@insurance_id.pdf"
```

**Response:**
```json
{
  "documents": [
    {
      "filename": "medical_bill.pdf",
      "document_type": "bill",
      "extracted_data": {
        "patient_name": "John Doe",
        "patient_id": "P12345",
        "bill_number": "B-2024-001",
        "bill_date": "2024-01-15",
        "hospital_name": "City Hospital",
        "total_amount": 5000.0,
        "items": [
          {
            "description": "Room charges",
            "amount": 2000.0
          },
          {
            "description": "Surgery",
            "amount": 3000.0
          }
        ],
        "payment_status": "pending"
      },
      "confidence": null
    },
    {
      "filename": "discharge_summary.pdf",
      "document_type": "discharge_summary",
      "extracted_data": {
        "patient_name": "John Doe",
        "patient_id": "P12345",
        "admission_date": "2024-01-10",
        "discharge_date": "2024-01-15",
        "diagnosis": "Appendicitis",
        "procedures": ["Appendectomy"],
        "medications": ["Antibiotics", "Pain relievers"],
        "doctor_name": "Dr. Smith",
        "hospital_name": "City Hospital",
        "follow_up_required": true
      },
      "confidence": null
    },
    {
      "filename": "insurance_id.pdf",
      "document_type": "id_card",
      "extracted_data": {
        "patient_name": "John Doe",
        "patient_id": "P12345",
        "insurance_company": "HealthInsure Co",
        "policy_number": "POL-987654",
        "group_number": "GRP-001",
        "date_of_birth": "1990-05-15",
        "valid_from": "2024-01-01",
        "valid_until": "2024-12-31",
        "member_id": "M123456"
      },
      "confidence": null
    }
  ],
  "validation": {
    "missing_documents": [],
    "discrepancies": []
  },
  "claim_decision": {
    "status": "approved",
    "reason": "All required documents present with consistent information. Treatment and billing align appropriately.",
    "confidence": 0.95
  }
}
```

## AI Tool Usage

### Tools Used During Development

1. **Claude (Anthropic)** - Primary assistant for:
   - Architecture design
   - Code autocompletion
   - Prompt engineering
   - Documentation

2. **OpenAI GPT-4o-mini** - Runtime LLM for:
   - Document classification
   - Data extraction
   - Final decision making

### Prompt Engineering

#### 1. Classification Prompt

**Purpose**: Classify document type

**Prompt:**
```
Classify this medical document into ONE of these categories:
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
{"document_type": "bill|discharge_summary|id_card|pharmacy_bill|claim_form|other", "confidence": 0.95, "reasoning": "brief explanation"}
```

**Why This Works:**
- Clear category definitions with examples
- Explicit JSON format requirement
- Limited context (2000 chars) for speed
- Confidence scoring for downstream decisions

#### 2. Bill Extraction Prompt

**Purpose**: Extract structured data from medical bills

**Prompt:**
```
Extract structured data from this medical bill.

Document text:
{text}

Return ONLY valid JSON with these fields:
{
    "patient_name": "string or null",
    "patient_id": "string or null",
    "bill_number": "string or null",
    "bill_date": "YYYY-MM-DD or null",
    "hospital_name": "string or null",
    "total_amount": "float or null",
    "items": [
        {
            "description": "string",
            "amount": "float"
        }
    ],
    "payment_status": "paid|pending|partial or null"
}

Use null for any field you cannot extract.
```

**Why This Works:**
- Explicit schema definition
- Null handling for missing data
- Structured format prevents hallucination
- Date format standardization

#### 3. Final Decision Prompt

**Purpose**: Make claim approval decision

**Prompt:**
```
Review this medical claim and make a final decision.

Documents:
{json.dumps(docs_summary, indent=2)}

Consider:
1. Are all necessary documents present and complete?
2. Is the information consistent and reasonable?
3. Are there any red flags or suspicious patterns?
4. Is the claim amount reasonable for the treatment?

Respond with ONLY valid JSON:
{
    "status": "approved|rejected|manual_review",
    "reason": "detailed explanation of the decision",
    "confidence": 0.0-1.0
}
```

**Why This Works:**
- Structured decision framework
- Clear evaluation criteria
- Three-tier decision system
- Explanation requirement for transparency

### Prompt Design Principles

1. **Explicit JSON Output**: Always specify exact JSON structure
2. **Null Handling**: Instruct model to use null for missing data
3. **Format Constraints**: Enforce date formats, enums, types
4. **Context Limitation**: Only pass relevant text to reduce tokens
5. **System Prompts**: Set expert persona for better results

## Project Structure

```
superclaims-backend/
├── main.py                  # FastAPI application
├── orchestrator.py          # Main processing coordinator
├── classifier.py            # Document classification
├── pdf_extractor.py         # PDF text extraction
├── llm_client.py           # LLM API wrapper
├── validator.py            # Cross-document validation
├── decision_maker.py       # Final claim decision
├── models.py               # Pydantic models
├── config.py               # Configuration management
├── agents/
│   ├── __init__.py
│   ├── base_agent.py       # Abstract agent class
│   ├── bill_agent.py       # Medical bill processor
│   ├── discharge_agent.py  # Discharge summary processor
│   ├── id_agent.py         # ID card processor
│   ├── pharmacy_agent.py   # Pharmacy bill processor
│   └── claim_form_agent.py # Claim form processor
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## Design Decisions

### 1. Async Architecture
All I/O operations are async to handle multiple documents in parallel, improving throughput for multi-file claims.

### 2. Agent Pattern
Each document type has a dedicated agent with specialized extraction logic, making the system modular and extensible.

### 3. Two-Phase LLM Usage
- **Phase 1**: Classification and extraction (fast, structured)
- **Phase 2**: Final decision (complex reasoning)

### 4. Validation Layer
Rule-based validation catches obvious errors before expensive LLM decision-making.

### 5. Confidence Scoring
Decisions include confidence levels to enable downstream manual review routing.

## Limitations & Future Enhancements

### Current Limitations

1. **PDF Quality**: Relies on PyPDF2 which struggles with scanned/image PDFs
2. **LLM Costs**: Multiple LLM calls per document can be expensive
3. **Error Handling**: Limited retry logic for LLM API failures
4. **No Caching**: Repeated documents are reprocessed
5. **Single Provider**: Only supports OpenAI currently

### Future Enhancements

1. **OCR Integration**: Add Tesseract/Azure Vision for scanned documents
2. **Caching Layer**: Redis for document deduplication
3. **Multi-LLM Support**: Add Claude, Gemini as alternatives
4. **Batch Processing**: Queue system for high-volume processing
5. **Vector Store**: Semantic search for similar historical claims
6. **Audit Trail**: PostgreSQL for decision logging
7. **Real-time Updates**: WebSocket for progress tracking
8. **Advanced Validation**: ML-based fraud detection

## Testing

### Manual Testing

1. Prepare sample PDFs (bills, discharge summaries, ID cards)
2. Start the server: `uvicorn main:app --reload`
3. Test the endpoint:

```bash
curl -X POST "http://localhost:8000/process-claim" \
  -F "files=@test_bill.pdf" \
  -F "files=@test_discharge.pdf" \
  -F "files=@test_id.pdf"
```

### Health Check

```bash
curl http://localhost:8000/health
```

Expected response: `{"status": "healthy"}`

## Security Notes

- Never commit `.env` file
- API keys stored in environment variables
- Input validation on file types and sizes
- No user data persisted (stateless)

## Performance Considerations

- Average processing time: 5-10 seconds for 3 documents
- Parallel document processing reduces latency
- LLM calls are the main bottleneck
- Consider implementing request queuing for production

## License

MIT

## Author

Built for SuperClaims Backend Developer Assignment
# superclaims-api
