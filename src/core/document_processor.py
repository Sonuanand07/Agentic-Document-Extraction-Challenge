"""Main document processing orchestrator."""

import time
from typing import List, Optional, Dict, Any, Tuple
from PIL import Image
import io
import pdf2image
from src.agents.document_router import DocumentRouter
from src.agents.ocr_processor import OCRProcessor
from src.agents.extraction_agent import ExtractionAgent
from src.agents.validation_agent import ValidationAgent
from src.models.document_models import DocumentExtraction, ExtractedField, QualityAssurance
import logging

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main orchestrator for document processing pipeline."""
    
    def __init__(self):
        self.router = DocumentRouter()
        self.ocr_processor = OCRProcessor()
        self.extraction_agent = ExtractionAgent()
        self.validation_agent = ValidationAgent()
    
    def process_document(
        self, 
        file_data: bytes, 
        filename: str,
        custom_fields: Optional[List[str]] = None
    ) -> DocumentExtraction:
        """
        Process a document through the complete extraction pipeline.
        
        Args:
            file_data: Raw file bytes
            filename: Original filename
            custom_fields: Optional list of custom fields to extract
            
        Returns:
            DocumentExtraction with all results
        """
        start_time = time.time()
        
        try:
            # Step 1: Convert to image if PDF
            image_data, images = self._prepare_images(file_data, filename)
            
            if not images:
                raise ValueError("Could not process file - no valid images found")
            
            # Use first page/image for processing
            primary_image = images[0]
            
            # Step 2: Document type detection
            logger.info("Detecting document type...")
            doc_type, type_confidence, type_metadata = self.router.detect_document_type(image_data)
            
            # Step 3: OCR processing
            logger.info("Performing OCR...")
            ocr_data = self.ocr_processor.extract_text_with_boxes(primary_image)
            
            # Step 4: Get extraction schema
            schema = self.router.get_extraction_schema(doc_type)
            
            # Step 5: Structured extraction
            logger.info("Extracting structured data...")
            extracted_fields = self.extraction_agent.extract_structured_data(
                image_data, ocr_data, doc_type, schema, custom_fields
            )
            
            # Step 6: Validation and QA
            logger.info("Validating extraction...")
            qa_results = self.validation_agent.validate_extraction(extracted_fields, doc_type)
            
            # Step 7: Calculate overall confidence
            overall_confidence = self._calculate_overall_confidence(
                extracted_fields, type_confidence, ocr_data, qa_results
            )
            
            processing_time = time.time() - start_time
            
            # Create final result
            result = DocumentExtraction(
                doc_type=doc_type,
                fields=extracted_fields,
                overall_confidence=overall_confidence,
                qa=qa_results,
                processing_time=processing_time,
                metadata={
                    'filename': filename,
                    'type_detection': type_metadata,
                    'ocr_confidence': ocr_data.get('average_confidence', 0.0),
                    'num_pages': len(images)
                }
            )
            
            logger.info(f"Document processing completed in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Document processing failed: {str(e)}")
            # Return error result
            return DocumentExtraction(
                doc_type="invoice",  # Default
                fields=[],
                overall_confidence=0.0,
                qa=QualityAssurance(
                    failed_rules=["processing_error"],
                    notes=f"Processing failed: {str(e)}"
                ),
                processing_time=time.time() - start_time,
                metadata={'error': str(e), 'filename': filename}
            )
    
    def _prepare_images(self, file_data: bytes, filename: str) -> Tuple[bytes, List[Image.Image]]:
        """Convert file to images for processing."""
        try:
            if filename.lower().endswith('.pdf'):
                # Convert PDF to images
                images = pdf2image.convert_from_bytes(file_data, dpi=300)
                
                # Convert first page back to bytes for API calls
                img_byte_arr = io.BytesIO()
                images[0].save(img_byte_arr, format='JPEG', quality=95)
                image_data = img_byte_arr.getvalue()
                
                return image_data, images
            else:
                # Handle image files
                image = Image.open(io.BytesIO(file_data))
                
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Convert to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=95)
                image_data = img_byte_arr.getvalue()
                
                return image_data, [image]
                
        except Exception as e:
            logger.error(f"Image preparation failed: {str(e)}")
            return b'', []
    
    def _calculate_overall_confidence(
        self, 
        fields: List[ExtractedField], 
        type_confidence: float,
        ocr_data: Dict[str, Any],
        qa_results: QualityAssurance
    ) -> float:
        """Calculate overall confidence score."""
        if not fields:
            return 0.0
        
        # Factor 1: Average field confidence
        field_confidences = [f.confidence for f in fields]
        avg_field_confidence = sum(field_confidences) / len(field_confidences)
        
        # Factor 2: Document type confidence
        type_conf = type_confidence
        
        # Factor 3: OCR quality
        ocr_conf = ocr_data.get('average_confidence', 0.0)
        
        # Factor 4: Validation results
        validation_conf = qa_results.cross_validation_score
        
        # Factor 5: Number of extracted fields (completeness)
        completeness = min(len(fields) / 8.0, 1.0)  # Assume 8 fields is "complete"
        
        # Weighted combination
        overall_confidence = (
            avg_field_confidence * 0.35 +
            type_conf * 0.20 +
            ocr_conf * 0.20 +
            validation_conf * 0.15 +
            completeness * 0.10
        )
        
        return min(max(overall_confidence, 0.0), 1.0)
