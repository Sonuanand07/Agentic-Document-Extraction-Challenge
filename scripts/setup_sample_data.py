"""Script to download and organize sample documents for testing."""

import os
import requests
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_data_directory():
    """Create directory structure for sample documents."""
    
    data_dir = Path("sample_data")
    data_dir.mkdir(exist_ok=True)
    
    # Create subdirectories for each document type
    (data_dir / "invoices").mkdir(exist_ok=True)
    (data_dir / "medical_bills").mkdir(exist_ok=True)
    (data_dir / "prescriptions").mkdir(exist_ok=True)
    
    logger.info("Created sample data directory structure")
    
    # Create a README for sample data
    readme_content = """# Sample Data Directory

This directory contains sample documents for testing the extraction system.

## Structure:
- `invoices/` - Sample invoice documents
- `medical_bills/` - Sample medical bill documents  
- `prescriptions/` - Sample prescription documents

## Usage:
Upload these documents through the Streamlit interface to test extraction capabilities.

## Note:
These are sample documents for testing purposes only. Do not use real sensitive documents.
"""
    
    with open(data_dir / "README.md", "w") as f:
        f.write(readme_content)
    
    logger.info("Sample data directory setup complete")

if __name__ == "__main__":
    create_sample_data_directory()
