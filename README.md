# LogiExtract — AI Logistics Document Extraction Agent

An LLM-powered agentic pipeline that extracts structured fields from logistics documents (Bill of Lading, Invoice, Purchase Order) and validates them for compliance — built with LangGraph, FastAPI, React, and PostgreSQL.

---

## Architecture

```
PDF Upload → Text Extraction (pdfplumber)
           → LangGraph 5-Stage Pipeline:
               1. Scope Resolution    — Identifies doc type (B/L, Invoice, PO)
               2. Context Compilation — Selects the right extraction schema
               3. Schema Routing      — Routes to extract or error handler
               4. Plan + Execute      — GPT-4o-mini extracts all fields + confidence score
               5. Evidence Delivery   — Returns structured JSON with source snippets
           → Validation Agent        — Flags missing/mismatched fields
           → PostgreSQL              — Stores all records
           → React Frontend          — Displays results with validation report
```

This mirrors GoComet Nova's 5-stage agent architecture exactly.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| AI Agent | LangGraph + LangChain |
| LLM | OpenAI GPT-4o-mini |
| Backend | Python + FastAPI |
| PDF Parsing | pdfplumber |
| Database | PostgreSQL + SQLAlchemy |
| Frontend | React + Vite + Tailwind CSS |
| Containerisation | Docker + Docker Compose |

---

## Quickstart

### Prerequisites
- Docker & Docker Compose
- Gemini API key (free for testing)

### 1. Clone and configure
```bash
git clone <your-repo>
cd logistics-extractor

cp backend/.env.example backend/.env
# Edit backend/.env and add your OPENAI_API_KEY
```

### 2. Run everything
```bash
docker-compose up --build
```

### 3. Open
- **Frontend:** http://localhost:5173
- **API Docs:** http://localhost:8000/docs
- **Health check:** http://localhost:8000/health

---

## Without Docker (Local Dev)

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env
# Add your OPENAI_API_KEY to .env
# Make sure PostgreSQL is running locally

uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/extract` | Upload PDF → extract fields |
| `POST` | `/api/validate/{id}` | Upload PO PDF → validate invoice |
| `GET` | `/api/records` | List all extraction records |
| `GET` | `/api/records/{id}` | Get single record |
| `DELETE` | `/api/records/{id}` | Delete record |

Full interactive docs at: http://localhost:8000/docs

---

## What Gets Extracted

### Bill of Lading (19 fields)
Shipper, consignee, notify party, vessel name, voyage number, port of loading/discharge, cargo description, HS code, gross weight, B/L number, date of issue, freight terms, incoterms, and more.

### Invoice (14 fields)
Invoice number/date, seller/buyer details, PO reference, currency, total amount, line items, payment terms, bank details, country of origin.

### Purchase Order (10 fields)
PO number/date, buyer/supplier, delivery date, line items, total amount, currency, delivery address, payment terms.

---

## Validation Logic

1. **Standalone validation** — checks every document for missing critical fields and logical inconsistencies
2. **Invoice vs PO validation** — upload a matching PO to compare against an invoice; flags amount mismatches, party name differences, and missing references

---

## Deployment (Render) -backend

```bash
# Backend on render



Set environment variables:
- `GEMINI_API_KEY`
- `DATABASE_URL` 

---

## Resume Bullet Points 

> Built an LLM-powered logistics document extraction agent using **LangGraph + OpenAI GPT-4o-mini** — a 5-stage agentic pipeline (scope resolution → context compilation → schema routing → plan+execute → evidence delivery) that extracts 15+ structured fields from Bills of Lading, Invoices, and Purchase Orders with confidence scoring and cross-document validation.

> Designed a **FastAPI + PostgreSQL** backend with pdfplumber for text extraction, SQLAlchemy ORM for persistence, and a React + Vite frontend with drag-and-drop upload and real-time validation reports. Containerised the full stack with Docker Compose.
