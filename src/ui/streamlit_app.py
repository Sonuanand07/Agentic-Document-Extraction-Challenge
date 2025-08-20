"""Streamlit UI for the document extraction system."""

import streamlit as st
import json
import time
from typing import Optional
from src.core.document_processor import DocumentProcessor
from src.config import settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Agentic Document Extraction",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .confidence-bar {
        background-color: #f0f0f0;
        border-radius: 10px;
        padding: 2px;
        margin: 5px 0;
    }
    .confidence-fill {
        height: 20px;
        border-radius: 8px;
        text-align: center;
        line-height: 20px;
        color: white;
        font-weight: bold;
        font-size: 12px;
    }
    .field-container {
        border: 1px solid #ddd;
        border-radius: 5px;
        padding: 10px;
        margin: 5px 0;
        background-color: #f9f9f9;
    }
    .qa-passed {
        color: #28a745;
        font-weight: bold;
    }
    .qa-failed {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

def get_confidence_color(confidence: float) -> str:
    """Get color based on confidence score."""
    if confidence >= 0.8:
        return "#28a745"  # Green
    elif confidence >= 0.6:
        return "#ffc107"  # Yellow
    else:
        return "#dc3545"  # Red

def render_confidence_bar(confidence: float, label: str = "") -> None:
    """Render a confidence bar."""
    color = get_confidence_color(confidence)
    width = confidence * 100
    
    st.markdown(f"""
    <div class="confidence-bar">
        <div class="confidence-fill" style="background-color: {color}; width: {width}%;">
            {label} {confidence:.2f}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_extracted_field(field) -> None:
    """Render an extracted field with confidence."""
    st.markdown(f"""
    <div class="field-container">
        <strong>{field.name}:</strong> {field.value}
    </div>
    """, unsafe_allow_html=True)
    
    render_confidence_bar(field.confidence, "Confidence:")
    
    if field.validation_notes and field.validation_notes != "Valid":
        st.caption(f"⚠️ {field.validation_notes}")

def main():
    """Main Streamlit application."""
    
    # Header
    st.markdown('<h1 class="main-header">🤖 Agentic Document Extraction</h1>', unsafe_allow_html=True)
    
    st.markdown("""
    Upload a document (PDF or image) to extract structured data using AI agents.
    Supports **invoices**, **medical bills**, and **prescriptions**.
    """)
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input(
            "OpenAI API Key", 
            type="password",
            help="Enter your OpenAI API key for document processing"
        )
        
        if api_key:
            settings.openai_api_key = api_key
        
        # Custom fields
        st.subheader("Custom Fields (Optional)")
        custom_fields_text = st.text_area(
            "Additional fields to extract",
            placeholder="Enter field names, one per line\ne.g.:\ncompany_phone\nspecial_instructions",
            help="Specify additional fields you want to extract from the document"
        )
        
        custom_fields = [field.strip() for field in custom_fields_text.split('\n') if field.strip()] if custom_fields_text else None
        
        # Processing options
        st.subheader("Processing Options")
        show_debug = st.checkbox("Show debug information", value=False)
        auto_download = st.checkbox("Auto-download JSON results", value=False)
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📤 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a file",
            type=['pdf', 'png', 'jpg', 'jpeg'],
            help="Upload a PDF or image file (max 10MB)"
        )
        
        if uploaded_file is not None:
            # File info
            st.info(f"**File:** {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            
            # Display uploaded image/PDF
            if uploaded_file.type.startswith('image'):
                st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)
            else:
                st.success("PDF uploaded successfully!")
    
    with col2:
        st.subheader("🎯 Extraction Results")
        
        if uploaded_file is not None and settings.openai_api_key:
            
            if st.button("🚀 Process Document", type="primary"):
                
                with st.spinner("Processing document... This may take a few moments."):
                    try:
                        # Initialize processor
                        processor = DocumentProcessor()
                        
                        # Process document
                        file_data = uploaded_file.read()
                        result = processor.process_document(
                            file_data, 
                            uploaded_file.name,
                            custom_fields
                        )
                        
                        # Store result in session state
                        st.session_state.extraction_result = result
                        
                    except Exception as e:
                        st.error(f"Processing failed: {str(e)}")
                        logger.error(f"Processing error: {str(e)}")
        
        elif not settings.openai_api_key:
            st.warning("⚠️ Please enter your OpenAI API key in the sidebar to process documents.")
        
        elif uploaded_file is None:
            st.info("👆 Upload a document to get started.")
    
    # Display results if available
    if hasattr(st.session_state, 'extraction_result'):
        result = st.session_state.extraction_result
        
        st.markdown("---")
        st.subheader("📊 Extraction Results")
        
        # Overall metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Document Type", result.doc_type.replace('_', ' ').title())
        
        with col2:
            st.metric("Fields Extracted", len(result.fields))
        
        with col3:
            st.metric("Processing Time", f"{result.processing_time:.2f}s")
        
        with col4:
            st.metric("Overall Confidence", f"{result.overall_confidence:.2f}")
        
        # Overall confidence bar
        st.subheader("🎯 Overall Confidence")
        render_confidence_bar(result.overall_confidence, "Overall:")
        
        # Extracted fields
        if result.fields:
            st.subheader("📋 Extracted Fields")
            
            for field in result.fields:
                render_extracted_field(field)
        
        # Quality Assurance
        st.subheader("✅ Quality Assurance")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if result.qa.passed_rules:
                st.markdown("**Passed Rules:**")
                for rule in result.qa.passed_rules:
                    st.markdown(f'<span class="qa-passed">✅ {rule}</span>', unsafe_allow_html=True)
        
        with col2:
            if result.qa.failed_rules:
                st.markdown("**Failed Rules:**")
                for rule in result.qa.failed_rules:
                    st.markdown(f'<span class="qa-failed">❌ {rule}</span>', unsafe_allow_html=True)
        
        if result.qa.notes:
            st.info(f"**Notes:** {result.qa.notes}")
        
        # JSON Output
        st.subheader("📄 JSON Output")
        
        # Convert result to JSON
        result_dict = result.dict()
        json_str = json.dumps(result_dict, indent=2, default=str)
        
        st.code(json_str, language='json')
        
        # Download button
        st.download_button(
            label="📥 Download JSON",
            data=json_str,
            file_name=f"extraction_result_{int(time.time())}.json",
            mime="application/json"
        )
        
        # Debug information
        if show_debug:
            st.subheader("🔍 Debug Information")
            st.json(result.metadata)

if __name__ == "__main__":
    main()
