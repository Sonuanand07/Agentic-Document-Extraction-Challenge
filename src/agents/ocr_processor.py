"""OCR processing agent for document text extraction."""

import pytesseract
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)

class OCRProcessor:
    """Agent for OCR text extraction and preprocessing."""
    
    def __init__(self):
        self.config = "--oem 3 --psm 6"
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR results.
        """
        try:
            # Convert PIL to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Convert to grayscale
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Apply denoising
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding
            thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Morphological operations to clean up
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL
            return Image.fromarray(cleaned)
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {str(e)}, using original")
            return image
    
    def extract_text_with_boxes(self, image: Image.Image) -> Dict[str, Any]:
        """
        Extract text with bounding box information.
        
        Returns:
            Dictionary with text, confidence scores, and bounding boxes
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Get detailed OCR data
            ocr_data = pytesseract.image_to_data(
                processed_image, 
                config=self.config,
                output_type=pytesseract.Output.DICT
            )
            
            # Extract text with confidence and bounding boxes
            extracted_text = []
            word_boxes = []
            
            for i in range(len(ocr_data['text'])):
                text = ocr_data['text'][i].strip()
                confidence = int(ocr_data['conf'][i])
                
                if text and confidence > 30:  # Filter low confidence text
                    x = ocr_data['left'][i]
                    y = ocr_data['top'][i]
                    w = ocr_data['width'][i]
                    h = ocr_data['height'][i]
                    
                    extracted_text.append(text)
                    word_boxes.append({
                        'text': text,
                        'confidence': confidence / 100.0,
                        'bbox': {
                            'x1': x,
                            'y1': y,
                            'x2': x + w,
                            'y2': y + h
                        }
                    })
            
            # Get full text
            full_text = pytesseract.image_to_string(processed_image, config=self.config)
            
            return {
                'full_text': full_text,
                'word_boxes': word_boxes,
                'average_confidence': np.mean([box['confidence'] for box in word_boxes]) if word_boxes else 0.0
            }
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return {
                'full_text': "",
                'word_boxes': [],
                'average_confidence': 0.0
            }
    
    def detect_tables(self, image: Image.Image) -> List[Dict[str, Any]]:
        """
        Detect and extract table structures from the image.
        """
        try:
            # Convert to OpenCV format
            opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            gray = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2GRAY)
            
            # Detect horizontal and vertical lines
            horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
            vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
            
            # Apply morphological operations
            horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
            vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
            
            # Combine lines
            table_mask = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
            
            # Find contours (potential table regions)
            contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            tables = []
            for contour in contours:
                x, y, w, h = cv2.boundingRect(contour)
                if w > 100 and h > 50:  # Filter small regions
                    tables.append({
                        'bbox': {'x1': x, 'y1': y, 'x2': x + w, 'y2': y + h},
                        'area': w * h
                    })
            
            return sorted(tables, key=lambda t: t['area'], reverse=True)
            
        except Exception as e:
            logger.error(f"Table detection failed: {str(e)}")
            return []
