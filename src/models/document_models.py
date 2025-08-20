"""Pydantic models for document extraction."""

from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field

class BoundingBox(BaseModel):
    """Bounding box coordinates."""
    x1: float
    y1: float
    x2: float
    y2: float

class FieldSource(BaseModel):
    """Source information for extracted field."""
    page: int
    bbox: Optional[BoundingBox] = None
    ocr_confidence: Optional[float] = None

class ExtractedField(BaseModel):
    """Individual extracted field with confidence."""
    name: str
    value: str
    confidence: float = Field(ge=0.0, le=1.0)
    source: Optional[FieldSource] = None
    validation_passed: bool = True
    validation_notes: Optional[str] = None

class QualityAssurance(BaseModel):
    """Quality assurance results."""
    passed_rules: List[str] = []
    failed_rules: List[str] = []
    notes: str = ""
    cross_validation_score: float = 0.0

class DocumentExtraction(BaseModel):
    """Complete document extraction result."""
    doc_type: Literal["invoice", "medical_bill", "prescription"]
    fields: List[ExtractedField]
    overall_confidence: float = Field(ge=0.0, le=1.0)
    qa: QualityAssurance
    processing_time: Optional[float] = None
    metadata: Dict[str, Any] = {}

# Document type specific schemas
class InvoiceFields(BaseModel):
    """Standard invoice fields."""
    invoice_number: Optional[str] = None
    date: Optional[str] = None
    vendor_name: Optional[str] = None
    vendor_address: Optional[str] = None
    customer_name: Optional[str] = None
    customer_address: Optional[str] = None
    subtotal: Optional[str] = None
    tax: Optional[str] = None
    total: Optional[str] = None
    line_items: Optional[List[Dict[str, str]]] = None

class MedicalBillFields(BaseModel):
    """Standard medical bill fields."""
    patient_name: Optional[str] = None
    patient_id: Optional[str] = None
    date_of_service: Optional[str] = None
    provider_name: Optional[str] = None
    provider_address: Optional[str] = None
    diagnosis_codes: Optional[List[str]] = None
    procedure_codes: Optional[List[str]] = None
    charges: Optional[str] = None
    insurance_paid: Optional[str] = None
    patient_responsibility: Optional[str] = None

class PrescriptionFields(BaseModel):
    """Standard prescription fields."""
    patient_name: Optional[str] = None
    prescriber_name: Optional[str] = None
    medication_name: Optional[str] = None
    dosage: Optional[str] = None
    quantity: Optional[str] = None
    refills: Optional[str] = None
    date_prescribed: Optional[str] = None
    pharmacy_name: Optional[str] = None
    rx_number: Optional[str] = None
