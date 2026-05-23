from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class DocType(str, Enum):
    BILL_OF_LADING = "bill_of_lading"
    INVOICE = "invoice"
    PURCHASE_ORDER = "purchase_order"

class BillOfLadingFields(BaseModel):
    shipper_name: Optional[str] = None
    shipper_address: Optional[str] = None
    consignee_name: Optional[str] = None
    consignee_address: Optional[str] = None
    notify_party: Optional[str] = None
    vessel_name: Optional[str] = None
    voyage_number: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    place_of_delivery: Optional[str] = None
    cargo_description: Optional[str] = None
    hs_code: Optional[str] = None
    gross_weight: Optional[str] = None
    measurement: Optional[str] = None
    number_of_packages: Optional[str] = None
    bl_number: Optional[str] = None
    date_of_issue: Optional[str] = None
    freight_terms: Optional[str] = None  # Prepaid / Collect
    incoterms: Optional[str] = None

class InvoiceFields(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    po_reference: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    payment_terms: Optional[str] = None
    bank_details: Optional[str] = None
    hs_code: Optional[str] = None
    country_of_origin: Optional[str] = None

class PurchaseOrderFields(BaseModel):
    po_number: Optional[str] = None
    po_date: Optional[str] = None
    buyer_name: Optional[str] = None
    supplier_name: Optional[str] = None
    delivery_date: Optional[str] = None
    line_items: Optional[List[Dict[str, Any]]] = None
    total_amount: Optional[str] = None
    currency: Optional[str] = None
    delivery_address: Optional[str] = None
    payment_terms: Optional[str] = None

class ValidationIssue(BaseModel):
    field: str
    expected: str
    found: str
    severity: str  # "error" | "warning"

class ValidationResult(BaseModel):
    status: str
    matched_fields: List[str] = []
    mismatched_fields: List[ValidationIssue] = []
    missing_fields: List[str] = []
    summary: str

class ExtractionResponse(BaseModel):
    id: int
    filename: str
    doc_type: str
    extracted_fields: Dict[str, Any]
    confidence_score: float
    validation_status: str
    validation_result: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

class ExtractionListResponse(BaseModel):
    records: List[ExtractionResponse]
    total: int
