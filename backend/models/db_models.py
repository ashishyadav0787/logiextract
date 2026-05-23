from sqlalchemy import Column, Integer, String, DateTime, JSON, Float, Text, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class ValidationStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    MISMATCH = "mismatch"
    WARNING = "warning"

class ExtractionRecord(Base):
    __tablename__ = "extraction_records"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    doc_type = Column(String, nullable=False)  # "bill_of_lading" | "invoice" | "purchase_order"
    extracted_fields = Column(JSON, nullable=False)
    raw_text = Column(Text)
    confidence_score = Column(Float)
    validation_status = Column(Enum(ValidationStatus), default=ValidationStatus.PENDING)
    validation_result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
