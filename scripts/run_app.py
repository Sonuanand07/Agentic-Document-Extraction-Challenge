#!/usr/bin/env python3
"""
Script to run the Streamlit application and check for issues
"""

import subprocess
import sys
import os
import importlib.util

def check_imports():
    """Check if all required modules can be imported"""
    required_modules = [
        'streamlit',
        'openai', 
        'pytesseract',
        'PIL',
        'cv2',
        'pdf2image',
        'pydantic',
        'numpy'
    ]
    
    missing_modules = []
    
    for module in required_modules:
        try:
            if module == 'PIL':
                import PIL
            elif module == 'cv2':
                import cv2
            else:
                importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError as e:
            print(f"❌ {module}: {e}")
            missing_modules.append(module)
    
    return missing_modules

def check_tesseract():
    """Check if Tesseract is available"""
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract OCR version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract OCR not found: {e}")
        return False

def main():
    print("🔍 Checking application dependencies...")
    
    # Check Python modules
    missing = check_imports()
    if missing:
        print(f"\n❌ Missing modules: {', '.join(missing)}")
        print("Run: pip install -r requirements.txt")
        return False
    
    # Check Tesseract
    if not check_tesseract():
        print("\n❌ Please install Tesseract OCR")
        return False
    
    print("\n✅ All dependencies are available!")
    print("🚀 Starting Streamlit application...")
    
    # Run the app
    try:
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py", 
            "--server.port", "8501",
            "--server.address", "0.0.0.0"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode != 0:
            print(f"❌ Streamlit failed to start:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("✅ Streamlit started successfully (timed out waiting, which is expected)")
        return True
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
