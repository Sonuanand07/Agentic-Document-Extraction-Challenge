#!/usr/bin/env python3
"""
Main entry point for the Agentic Document Extraction System
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import openai
        import pytesseract
        import PIL
        import cv2
        print("✅ All Python dependencies are installed")
    except ImportError as e:
        print(f"❌ Missing Python dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False
    
    # Check Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract OCR is installed")
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        print("Please install Tesseract OCR:")
        print("  Ubuntu/Debian: sudo apt-get install tesseract-ocr")
        print("  macOS: brew install tesseract")
        print("  Windows: Download from GitHub releases")
        return False
    
    return True

def main():
    """Main function to run the application"""
    print("🚀 Starting Agentic Document Extraction System...")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  OpenAI API key not found in environment variables")
        print("You can set it in the Streamlit sidebar or add it to .env file")
    
    # Run Streamlit app
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "streamlit_app.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Streamlit: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Shutting down...")

if __name__ == "__main__":
    main()
