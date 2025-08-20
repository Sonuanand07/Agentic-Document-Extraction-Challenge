"""Document type detection and routing agent."""

import base64
from typing import Tuple, Dict, Any
from openai import OpenAI
from src.config import settings
import logging

logger = logging.getLogger(__name__)

class DocumentRouter:
    """Agent for detecting document type and routing to appropriate processor."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        
    def detect_document_type(self, image_data: bytes) -> Tuple[str, float, Dict[str, Any]]:
        """
        Detect document type using GPT-4 Vision.
        
        Returns:
            Tuple of (document_type, confidence, metadata)
        """
        try:
            # Encode image to base64
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            prompt = """
            Analyze this document image and determine its type. Look for key visual indicators:
            
            INVOICE indicators:
            - "Invoice" header or title
            - Invoice number
            - Vendor/company information
            - Line items with quantities and prices
            - Subtotal, tax, total amounts
            - Payment terms
            
            MEDICAL_BILL indicators:
            - Hospital/clinic letterhead
            - Patient information
            - Date of service
            - Medical procedure codes (CPT codes)
            - Diagnosis codes (ICD codes)
            - Insurance information
            - Charges and payments
            
            PRESCRIPTION indicators:
            - "Rx" symbol or "Prescription" header
            - Prescriber/doctor information
            - Patient name and DOB
            - Medication names
            - Dosage instructions
            - DEA number
            - Pharmacy information
            
            Respond with ONLY a JSON object in this exact format:
            {
                "document_type": "invoice|medical_bill|prescription",
                "confidence": 0.95,
                "reasoning": "Brief explanation of key indicators found",
                "key_indicators": ["list", "of", "visual", "clues"]
            }
            """
            
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            
            # Parse JSON response
            import json
            parsed_result = json.loads(result)
            
            doc_type = parsed_result["document_type"]
            confidence = parsed_result["confidence"]
            metadata = {
                "reasoning": parsed_result.get("reasoning", ""),
                "key_indicators": parsed_result.get("key_indicators", [])
            }
            
            logger.info(f"Document type detected: {doc_type} (confidence: {confidence})")
            return doc_type, confidence, metadata
            
        except Exception as e:
            logger.error(f"Error in document type detection: {str(e)}")
            # Fallback to invoice as default
            return "invoice", 0.3, {"error": str(e)}
    
    def get_extraction_schema(self, doc_type: str) -> Dict[str, Any]:
        """Get the appropriate extraction schema for document type."""
        
        schemas = {
            "invoice": {
                "invoice_number": "string",
                "date": "date (MM/DD/YYYY or DD/MM/YYYY)",
                "vendor_name": "string",
                "vendor_address": "string",
                "customer_name": "string", 
                "customer_address": "string",
                "subtotal": "monetary amount",
                "tax": "monetary amount",
                "total": "monetary amount",
                "line_items": "array of {description, quantity, unit_price, total}"
            },
            "medical_bill": {
                "patient_name": "string",
                "patient_id": "string",
                "date_of_service": "date",
                "provider_name": "string",
                "provider_address": "string",
                "diagnosis_codes": "array of ICD codes",
                "procedure_codes": "array of CPT codes", 
                "charges": "monetary amount",
                "insurance_paid": "monetary amount",
                "patient_responsibility": "monetary amount"
            },
            "prescription": {
                "patient_name": "string",
                "prescriber_name": "string",
                "medication_name": "string",
                "dosage": "string with units",
                "quantity": "number",
                "refills": "number",
                "date_prescribed": "date",
                "pharmacy_name": "string",
                "rx_number": "string"
            }
        }
        
        return schemas.get(doc_type, schemas["invoice"])
