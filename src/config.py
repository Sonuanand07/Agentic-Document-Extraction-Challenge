"""Configuration settings for the document extraction system."""

import os
from typing import Dict, List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings."""
    
    # OpenAI Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-vision-preview"
    openai_text_model: str = "gpt-4-turbo-preview"
    
    # Document Processing
    max_file_size_mb: int = 10
    supported_formats: List[str] = [".pdf", ".png", ".jpg", ".jpeg"]
    
    # OCR Configuration
    tesseract_config: str = "--oem 3 --psm 6"
    
    # Confidence Thresholds
    min_field_confidence: float = 0.5
    min_overall_confidence: float = 0.7
    
    # Validation Rules
    validation_rules: Dict[str, str] = {
        "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
        "phone": r'^\+?[\d\s\-$$$$]{10,}$',
        "date": r'^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$',
        "amount": r'^\$?\d+\.?\d{0,2}$'
    }
    
    class Config:
        env_file = ".env"

# Global settings instance
settings = Settings()
