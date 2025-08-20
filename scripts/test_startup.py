#!/usr/bin/env python3
"""
Test script to verify the application can start properly
"""

import sys
import os
import importlib.util
import traceback

def test_imports():
    """Test all critical imports"""
    print("Testing imports...")
    
    try:
        # Test core dependencies
        import streamlit
        print("✅ streamlit")
        
        import openai
        print("✅ openai")
        
        import pytesseract
        print("✅ pytesseract")
        
        import PIL
        print("✅ PIL")
        
        import cv2
        print("✅ cv2")
        
        import pdf2image
        print("✅ pdf2image")
        
        import pydantic
        print("✅ pydantic")
        
        # Test project modules
        from src.config import settings
        print("✅ src.config")
        
        from src.models.document_models import DocumentExtraction
        print("✅ src.models.document_models")
        
        from src.agents.document_router import DocumentRouter
        print("✅ src.agents.document_router")
        
        from src.agents.ocr_processor import OCRProcessor
        print("✅ src.agents.ocr_processor")
        
        from src.agents.extraction_agent import ExtractionAgent
        print("✅ src.agents.extraction_agent")
        
        from src.agents.validation_agent import ValidationAgent
        print("✅ src.agents.validation_agent")
        
        from src.core.document_processor import DocumentProcessor
        print("✅ src.core.document_processor")
        
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        traceback.print_exc()
        return False

def test_tesseract():
    """Test Tesseract OCR availability"""
    print("\nTesting Tesseract OCR...")
    
    try:
        import pytesseract
        version = pytesseract.get_tesseract_version()
        print(f"✅ Tesseract version: {version}")
        return True
    except Exception as e:
        print(f"❌ Tesseract not available: {e}")
        return False

def test_config():
    """Test configuration loading"""
    print("\nTesting configuration...")
    
    try:
        from src.config import settings
        print(f"✅ Config loaded")
        print(f"  - OpenAI model: {settings.openai_model}")
        print(f"  - Min field confidence: {settings.min_field_confidence}")
        print(f"  - Supported formats: {settings.supported_formats}")
        return True
    except Exception as e:
        print(f"❌ Config failed: {e}")
        return False

def test_agent_initialization():
    """Test agent initialization without API key"""
    print("\nTesting agent initialization...")
    
    try:
        # Test OCR processor (doesn't need API key)
        from src.agents.ocr_processor import OCRProcessor
        ocr = OCRProcessor()
        print("✅ OCR Processor initialized")
        
        # Test validation agent
        from src.agents.validation_agent import ValidationAgent
        validator = ValidationAgent()
        print("✅ Validation Agent initialized")
        
        # Test document router (will fail without API key, but should initialize)
        from src.agents.document_router import DocumentRouter
        try:
            router = DocumentRouter()
            print("✅ Document Router initialized")
        except Exception as e:
            print(f"⚠️  Document Router needs API key: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent initialization failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🔍 Testing Agentic Document Extraction System startup...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Tesseract Test", test_tesseract),
        ("Configuration Test", test_config),
        ("Agent Initialization Test", test_agent_initialization)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Running {test_name}")
        print('='*50)
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("TEST SUMMARY")
    print('='*50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The application should start successfully.")
        print("\nTo run the application:")
        print("  streamlit run streamlit_app.py")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix the issues above.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
