"""Main extraction agent using LLM for structured data extraction."""

import json
import base64
from typing import Dict, List, Any, Optional
from openai import OpenAI
from src.config import settings
from src.models.document_models import ExtractedField, FieldSource, BoundingBox
import logging
import re

logger = logging.getLogger(__name__)

class ExtractionAgent:
    """Agent for structured data extraction using LLM."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
    
    def extract_structured_data(
        self, 
        image_data: bytes, 
        ocr_data: Dict[str, Any], 
        doc_type: str,
        schema: Dict[str, str],
        custom_fields: Optional[List[str]] = None
    ) -> List[ExtractedField]:
        """
        Extract structured data using GPT-4 Vision and OCR data.
        """
        try:
            # Prepare the extraction schema
            extraction_schema = schema.copy()
            if custom_fields:
                for field in custom_fields:
                    if field not in extraction_schema:
                        extraction_schema[field] = "string"
            
            # Create extraction prompt
            prompt = self._create_extraction_prompt(doc_type, extraction_schema, ocr_data)
            
            # Encode image
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Call GPT-4 Vision
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
                max_tokens=2000,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            
            # Parse the JSON response
            extracted_data = json.loads(result)
            
            # Convert to ExtractedField objects with confidence scoring
            fields = []
            for field_name, field_data in extracted_data.get("fields", {}).items():
                if field_data.get("value"):
                    # Calculate confidence based on multiple factors
                    confidence = self._calculate_field_confidence(
                        field_name, 
                        field_data, 
                        ocr_data,
                        doc_type
                    )
                    
                    # Find source information from OCR data
                    source = self._find_field_source(field_data.get("value"), ocr_data)
                    
                    field = ExtractedField(
                        name=field_name,
                        value=field_data["value"],
                        confidence=confidence,
                        source=source
                    )
                    fields.append(field)
            
            return fields
            
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return []
    
    def _create_extraction_prompt(self, doc_type: str, schema: Dict[str, str], ocr_data: Dict[str, Any]) -> str:
        """Create extraction prompt for the LLM."""
        
        ocr_text = ocr_data.get('full_text', '')[:2000]  # Limit OCR text length
        
        prompt = f"""
        You are an expert document extraction agent. Extract structured data from this {doc_type} document.
        
        OCR Text (for reference):
        {ocr_text}
        
        Extract the following fields according to the schema:
        {json.dumps(schema, indent=2)}
        
        IMPORTANT INSTRUCTIONS:
        1. Look carefully at both the image and OCR text
        2. For each field, provide the exact value found in the document
        3. If a field is not found or unclear, set value to null
        4. For monetary amounts, include currency symbol if present
        5. For dates, preserve the original format found
        6. For line items (if applicable), extract as structured array
        
        Respond with ONLY a JSON object in this exact format:
        {{
            "fields": {{
                "field_name": {{
                    "value": "extracted_value_or_null",
                    "extraction_confidence": 0.95,
                    "reasoning": "brief explanation of how this was found"
                }}
            }}
        }}
        
        Be precise and conservative with confidence scores. Use 0.9+ only for clearly visible, unambiguous text.
        """
        
        return prompt
    
    def _calculate_field_confidence(
        self, 
        field_name: str, 
        field_data: Dict[str, Any], 
        ocr_data: Dict[str, Any],
        doc_type: str
    ) -> float:
        """
        Calculate confidence score for extracted field using multiple factors.
        """
        base_confidence = field_data.get("extraction_confidence", 0.5)
        
        # Factor 1: OCR confidence for the specific text
        ocr_confidence = self._get_ocr_confidence_for_text(
            field_data.get("value", ""), 
            ocr_data
        )
        
        # Factor 2: Field type validation
        validation_confidence = self._validate_field_format(field_name, field_data.get("value", ""))
        
        # Factor 3: Document type relevance
        relevance_confidence = self._get_field_relevance(field_name, doc_type)
        
        # Weighted combination
        final_confidence = (
            base_confidence * 0.4 +
            ocr_confidence * 0.3 +
            validation_confidence * 0.2 +
            relevance_confidence * 0.1
        )
        
        return min(max(final_confidence, 0.0), 1.0)
    
    def _get_ocr_confidence_for_text(self, text: str, ocr_data: Dict[str, Any]) -> float:
        """Get OCR confidence for specific text."""
        if not text or not ocr_data.get('word_boxes'):
            return 0.5
        
        # Find matching words in OCR data
        text_words = text.lower().split()
        matching_confidences = []
        
        for box in ocr_data['word_boxes']:
            box_text = box['text'].lower()
            if any(word in box_text for word in text_words):
                matching_confidences.append(box['confidence'])
        
        return sum(matching_confidences) / len(matching_confidences) if matching_confidences else 0.5
    
    def _validate_field_format(self, field_name: str, value: str) -> float:
        """Validate field format and return confidence."""
        if not value:
            return 0.0
        
        # Check against validation rules
        for rule_type, pattern in settings.validation_rules.items():
            if rule_type in field_name.lower():
                if re.match(pattern, value):
                    return 0.9
                else:
                    return 0.3
        
        # Basic validation for common field types
        if 'amount' in field_name.lower() or 'total' in field_name.lower():
            if re.match(r'^\$?\d+\.?\d{0,2}$', value):
                return 0.8
            return 0.4
        
        if 'date' in field_name.lower():
            if re.match(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', value):
                return 0.8
            return 0.4
        
        return 0.6  # Default confidence for text fields
    
    def _get_field_relevance(self, field_name: str, doc_type: str) -> float:
        """Get field relevance score based on document type."""
        relevance_map = {
            "invoice": ["invoice_number", "vendor_name", "total", "date", "customer_name"],
            "medical_bill": ["patient_name", "provider_name", "charges", "date_of_service"],
            "prescription": ["patient_name", "medication_name", "prescriber_name", "dosage"]
        }
        
        relevant_fields = relevance_map.get(doc_type, [])
        return 0.9 if field_name in relevant_fields else 0.7
    
    def _find_field_source(self, value: str, ocr_data: Dict[str, Any]) -> Optional[FieldSource]:
        """Find source location of extracted field in OCR data."""
        if not value or not ocr_data.get('word_boxes'):
            return None
        
        # Find the best matching word box
        best_match = None
        best_score = 0
        
        for box in ocr_data['word_boxes']:
            # Simple text matching - could be improved with fuzzy matching
            if value.lower() in box['text'].lower() or box['text'].lower() in value.lower():
                score = len(box['text']) / len(value) if len(value) > 0 else 0
                if score > best_score:
                    best_score = score
                    best_match = box
        
        if best_match:
            bbox = BoundingBox(
                x1=best_match['bbox']['x1'],
                y1=best_match['bbox']['y1'],
                x2=best_match['bbox']['x2'],
                y2=best_match['bbox']['y2']
            )
            return FieldSource(
                page=1,  # Assuming single page for now
                bbox=bbox,
                ocr_confidence=best_match['confidence']
            )
        
        return None
