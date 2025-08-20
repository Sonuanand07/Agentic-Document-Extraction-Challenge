"""Configuration settings for the document extraction system."""

import os
from typing import Dict, List

class Config:
    """Application configuration."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4-vision-preview")
    OPENAI_TEXT_MODEL: str = os.getenv("OPENAI_TEXT_MODEL", "gpt-4-turbo-preview")
    
    # Document Processing
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "10"))
    SUPPORTED_FORMATS: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    
    # OCR Configuration
    TESSERACT_CONFIG: str = "--oem 3 --psm 6"
    
    # Confidence Thresholds
    MIN_FIELD_CONFIDENCE: float = float(os.getenv("MIN_FIELD_CONFIDENCE", "0.5"))
    MIN_OVERALL_CONFIDENCE: float = float(os.getenv("MIN_OVERALL_CONFIDENCE", "0.7"))
    
    # Validation Rules
    VALIDATION_RULES: Dict[str, str] = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone": r'^\+?[\d\s\-()]{10,}$',
        "date": r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$',
        "amount": r'^\$?\d+\.?\d{0,2}$'
    }

# Create a settings instance for backward compatibility
class Settings:
    def __init__(self):
        self.openai_api_key = Config.OPENAI_API_KEY
        self.openai_model = Config.OPENAI_MODEL
        self.openai_text_model = Config.OPENAI_TEXT_MODEL
        self.max_file_size_mb = Config.MAX_FILE_SIZE_MB
        self.supported_formats = Config.SUPPORTED_FORMATS
        self.tesseract_config = Config.TESSERACT_CONFIG
        self.min_field_confidence = Config.MIN_FIELD_CONFIDENCE
        self.min_overall_confidence = Config.MIN_OVERALL_CONFIDENCE
        self.validation_rules = Config.VALIDATION_RULES

# Global settings instance
settings = Settings()
