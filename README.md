# superclaims-api

Upload the PDFs for a medical insurance claim (hospital bill, discharge summary, insurance ID, pharmacy bill, claim form) and get back a decision: `approved`, `rejected` or `manual_review`, with the reason and the data pulled out of each document.

It is a FastAPI service. An LLM sorts and reads the documents; plain code checks them against each other; the LLM only gets the final say when the code finds nothing wrong.

Built as a take-home assignment for SuperClaims.

## How a claim is processed

```
POST /process-claim  (several PDFs)
        |
        v   all files at once (asyncio.gather)
  extract text with PyPDF2
  classify: bill | discharge_summary | id_card | pharmacy_bill | claim_form | other   (LLM)
  extract fields with the agent for that type                                       (LLM)
        |
        v
  validate (code only)
    - missing documents: bill, ID card and discharge summary are required
    - patient name and patient ID must match across documents
    - admission date must not be after discharge date
    - claim form amount must equal the bill total
        |
        v
  decide
    missing document            -> rejected        (no LLM call)
    name / ID / date mismatch   -> rejected        (no LLM call)
    any other mismatch          -> manual_review   (no LLM call)
    everything checks out       -> LLM reviews all extracted data and decides
```

The order is deliberate. Missing paperwork and mismatched patient details are cheap to catch with code and should never depend on how a model feels that day. The model is used where judgement helps: reading messy documents, and asking whether a clean-looking claim is reasonable.

Each document type has its own agent in `agents/` with a fixed JSON schema. For example, the bill agent returns patient name and ID, bill number and date, hospital, line items and total. Fields the model cannot find come back as `null`.

## Quickstart

You need Python 3.10+ and a [Groq API key](https://console.groq.com/keys).

```bash
git clone https://github.com/Rakshit-gen/superclaims-api.git
cd superclaims-api
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env     # set GROQ_API_KEY
uvicorn main:app --reload
```

Or `docker-compose up --build`.

Try it with the sample PDFs in the repo:

```bash
curl -X POST http://localhost:8000/process-claim \
  -F "files=@sample_medical_bill.pdf" \
  -F "files=@sample_discharge_summary.pdf" \
  -F "files=@sample_insurance_id.pdf"
```

`python generate_samples.py` recreates those PDFs if you want to edit them.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `GROQ_API_KEY` | required | Groq key. Calls go to Groq's OpenAI-compatible endpoint |
| `LLM_MODEL` | `llama-3.1-70b-versatile` in code, `llama-3.3-70b-versatile` in `.env.example` | Model for every step. Use the 3.3 one; the 3.1 model has been retired |
| `MAX_FILE_SIZE_MB` | 10 | Read from config but not enforced yet |

## API

| Method | Path | What it does |
|---|---|---|
| `POST` | `/process-claim` | Multipart upload, field name `files`, one or more `.pdf` files |
| `GET` | `/health` | `{"status": "healthy"}` |

Response, trimmed:

```json
{
  "documents": [
    {
      "filename": "sample_medical_bill.pdf",
      "document_type": "bill",
      "extracted_data": {
        "patient_name": "John Doe",
        "bill_date": "2024-01-15",
        "total_amount": 5000.0,
        "items": [{"description": "Surgery", "amount": 3000.0}]
      }
    }
  ],
  "validation": {"missing_documents": [], "discrepancies": []},
  "claim_decision": {
    "status": "approved",
    "reason": "All required documents present and consistent...",
    "confidence": 0.95
  }
}
```

## Layout

```
main.py             FastAPI app and upload handling
orchestrator.py     runs extract, classify, extract-fields per file, then validate and decide
pdf_extractor.py    PyPDF2 text extraction
classifier.py       LLM document type classification (first 2,000 chars)
agents/             one extraction agent per document type
validator.py        rule-based completeness and consistency checks
decision_maker.py   rules first, LLM last
llm_client.py       thin httpx client for Groq, strips code fences before parsing JSON
models.py           Pydantic models
```

## Limits

- PyPDF2 only reads text layers. Scanned PDFs come back empty and get classified as `other`.
- Name matching is exact after lowercasing, so "John Doe" and "John A. Doe" count as a mismatch and reject the claim.
- Dates are compared as strings, which only works because the extraction prompt asks for `YYYY-MM-DD`.
- No retries on LLM errors. One failed call fails the whole request with a 500.
- Nothing is stored. Each request is processed and forgotten.
