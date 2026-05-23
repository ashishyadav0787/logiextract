from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
import json

from db.database import get_db
from models.db_models import ExtractionRecord, ValidationStatus
from models.schemas import ExtractionResponse, ExtractionListResponse
from agents.extraction_agent import run_extraction
from agents.validation_agent import validate_against_po, quick_field_validate
from agents.pdf_utils import extract_text_from_pdf, validate_pdf

router = APIRouter(prefix="/api", tags=["extraction"])


@router.post("/extract", response_model=ExtractionResponse)
async def extract_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PDF (Bill of Lading, Invoice, or Purchase Order).
    The LangGraph agent pipeline extracts all structured fields.
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    file_bytes = await file.read()

    if not validate_pdf(file_bytes):
        raise HTTPException(status_code=400, detail="Invalid PDF file")

    # Extract text from PDF
    try:
        raw_text, _ = extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Could not read PDF: {str(e)}")

    if not raw_text.strip():
        raise HTTPException(status_code=422, detail="PDF appears to be empty or scanned (no extractable text)")

    # Run the LangGraph extraction pipeline
    try:
        result = run_extraction(raw_text, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")

    # Run standalone validation
    validation_result = None
    validation_status = ValidationStatus.PENDING

    if result.get("extracted_fields"):
        validation_result = quick_field_validate(
            result["extracted_fields"],
            result.get("doc_type", "unknown")
        )
        status_map = {
            "matched": ValidationStatus.MATCHED,
            "mismatch": ValidationStatus.MISMATCH,
            "warning": ValidationStatus.WARNING,
        }
        validation_status = status_map.get(
            validation_result.get("status", "warning"),
            ValidationStatus.WARNING
        )

    # Save to database
    record = ExtractionRecord(
        filename=file.filename,
        doc_type=result.get("doc_type", "unknown"),
        extracted_fields=result.get("extracted_fields", {}),
        raw_text=raw_text[:5000],  # Store first 5k chars
        confidence_score=result.get("confidence_score", 0.0),
        validation_status=validation_status,
        validation_result=validation_result
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return ExtractionResponse(
        id=record.id,
        filename=record.filename,
        doc_type=record.doc_type,
        extracted_fields=record.extracted_fields,
        confidence_score=record.confidence_score or 0.0,
        validation_status=record.validation_status.value,
        validation_result=record.validation_result,
        created_at=record.created_at
    )


@router.post("/validate/{record_id}", response_model=ExtractionResponse)
async def validate_against_purchase_order(
    record_id: int,
    po_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Validate an already-extracted Invoice against a Purchase Order PDF.
    Upload the PO PDF and it will be extracted + compared against the invoice.
    """
    record = db.query(ExtractionRecord).filter(ExtractionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    if record.doc_type != "invoice":
        raise HTTPException(status_code=400, detail="Validation requires an invoice record")

    # Extract PO
    po_bytes = await po_file.read()
    po_text, _ = extract_text_from_pdf(po_bytes)
    po_result = run_extraction(po_text, po_file.filename)

    if po_result.get("doc_type") != "purchase_order":
        raise HTTPException(status_code=400, detail="Uploaded file does not appear to be a Purchase Order")

    # Validate invoice against PO
    validation_result = validate_against_po(
        invoice_fields=record.extracted_fields,
        po_fields=po_result.get("extracted_fields", {})
    )

    status_map = {
        "matched": ValidationStatus.MATCHED,
        "mismatch": ValidationStatus.MISMATCH,
        "warning": ValidationStatus.WARNING,
    }
    record.validation_status = status_map.get(
        validation_result.get("status", "warning"),
        ValidationStatus.WARNING
    )
    record.validation_result = validation_result
    db.commit()
    db.refresh(record)

    return ExtractionResponse(
        id=record.id,
        filename=record.filename,
        doc_type=record.doc_type,
        extracted_fields=record.extracted_fields,
        confidence_score=record.confidence_score or 0.0,
        validation_status=record.validation_status.value,
        validation_result=record.validation_result,
        created_at=record.created_at
    )


@router.get("/records", response_model=ExtractionListResponse)
def list_records(
    doc_type: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all extraction records with optional filter by doc type."""
    query = db.query(ExtractionRecord)
    if doc_type:
        query = query.filter(ExtractionRecord.doc_type == doc_type)

    total = query.count()
    records = query.order_by(ExtractionRecord.created_at.desc()).offset(skip).limit(limit).all()

    return ExtractionListResponse(
        records=[
            ExtractionResponse(
                id=r.id,
                filename=r.filename,
                doc_type=r.doc_type,
                extracted_fields=r.extracted_fields,
                confidence_score=r.confidence_score or 0.0,
                validation_status=r.validation_status.value,
                validation_result=r.validation_result,
                created_at=r.created_at
            ) for r in records
        ],
        total=total
    )


@router.get("/records/{record_id}", response_model=ExtractionResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    """Get a single extraction record by ID."""
    record = db.query(ExtractionRecord).filter(ExtractionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")

    return ExtractionResponse(
        id=record.id,
        filename=record.filename,
        doc_type=record.doc_type,
        extracted_fields=record.extracted_fields,
        confidence_score=record.confidence_score or 0.0,
        validation_status=record.validation_status.value,
        validation_result=record.validation_result,
        created_at=record.created_at
    )


@router.delete("/records/{record_id}")
def delete_record(record_id: int, db: Session = Depends(get_db)):
    """Delete an extraction record."""
    record = db.query(ExtractionRecord).filter(ExtractionRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted"}
