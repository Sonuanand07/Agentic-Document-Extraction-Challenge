import streamlit as st
import json
from PIL import Image
import io
import traceback

try:
    from src.core.document_processor import DocumentProcessor
    from src.config import settings
    PROCESSOR_AVAILABLE = True
except ImportError as e:
    st.error(f"❌ Import Error: {e}")
    st.error("Please ensure all dependencies are installed: pip install -r requirements.txt")
    PROCESSOR_AVAILABLE = False

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
    .confidence-high { color: #28a745; font-weight: bold; }
    .confidence-medium { color: #ffc107; font-weight: bold; }
    .confidence-low { color: #dc3545; font-weight: bold; }
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 Agentic Document Extraction System</h1>', unsafe_allow_html=True)
    
    if not PROCESSOR_AVAILABLE:
        st.error("❌ Document processor is not available. Please check the installation.")
        st.info("Run the following commands to fix:")
        st.code("pip install -r requirements.txt")
        return
    
    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        api_key = st.text_input("OpenAI API Key", type="password", 
                               help="Enter your OpenAI API key to enable document processing")
        
        if api_key:
            settings.openai_api_key = api_key
            st.success("✅ API Key configured")
        else:
            st.warning("⚠️ Please enter your OpenAI API Key to proceed")
        
        st.divider()
        
        # Processing options
        st.subheader("Processing Options")
        confidence_threshold = st.slider("Confidence Threshold", 0.0, 1.0, 0.6, 0.1)
        show_debug = st.checkbox("Show Debug Information", False)
        
        st.divider()
        
        # Supported document types
        st.subheader("📋 Supported Documents")
        st.write("• **Invoices** - Business bills, receipts")
        st.write("• **Medical Bills** - Hospital statements, claims")
        st.write("• **Prescriptions** - Medication orders")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📤 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a document file",
            type=['png', 'jpg', 'jpeg', 'pdf'],
            help="Upload an image or PDF of your document"
        )
        
        if uploaded_file is not None:
            # Display uploaded image
            if uploaded_file.type.startswith('image'):
                image = Image.open(uploaded_file)
                st.image(image, caption="Uploaded Document", use_column_width=True)
            else:
                st.info("📄 PDF uploaded - will be converted to image for processing")
    
    with col2:
        st.header("🔍 Processing Results")
        
        if uploaded_file is not None and api_key:
            if st.button("🚀 Process Document", type="primary"):
                with st.spinner("Processing document..."):
                    try:
                        # Initialize processor
                        processor = DocumentProcessor()
                        
                        # Process document
                        file_content = uploaded_file.read()
                        result = processor.process_document(file_content, uploaded_file.name)
                        
                        # Store results in session state
                        st.session_state.processing_result = result
                        st.success("✅ Document processed successfully!")
                        
                    except Exception as e:
                        st.error(f"❌ Processing failed: {str(e)}")
                        if show_debug:
                            st.code(traceback.format_exc())
        
        elif uploaded_file is not None and not api_key:
            st.warning("⚠️ Please enter your OpenAI API Key in the sidebar to process documents")
    
    # Display results if available
    if hasattr(st.session_state, 'processing_result'):
        result = st.session_state.processing_result
        
        st.divider()
        st.header("📊 Extraction Results")
        
        try:
            # Metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                confidence = getattr(result, 'overall_confidence', 0.0)
                confidence_class = get_confidence_class(confidence)
                st.markdown(f'<div class="metric-card"><h3>Overall Confidence</h3><p class="{confidence_class}">{confidence:.2%}</p></div>', 
                           unsafe_allow_html=True)
            
            with col2:
                doc_type = getattr(result, 'doc_type', 'Unknown')
                st.markdown(f'<div class="metric-card"><h3>Document Type</h3><p>{doc_type.title()}</p></div>', 
                           unsafe_allow_html=True)
            
            with col3:
                processing_time = getattr(result, 'processing_time', 0.0)
                st.markdown(f'<div class="metric-card"><h3>Processing Time</h3><p>{processing_time:.2f}s</p></div>', 
                           unsafe_allow_html=True)
            
            with col4:
                qa_results = getattr(result, 'qa', None)
                validation_status = "✅ Valid" if qa_results and not qa_results.failed_rules else "❌ Issues Found"
                st.markdown(f'<div class="metric-card"><h3>Validation</h3><p>{validation_status}</p></div>', 
                           unsafe_allow_html=True)
            
            # Extracted data
            st.subheader("📋 Extracted Fields")
            
            fields = getattr(result, 'fields', [])
            if fields:
                # Display fields in a table format
                for field in fields:
                    col1, col2, col3 = st.columns([2, 3, 1])
                    
                    with col1:
                        st.write(f"**{field.name.replace('_', ' ').title()}**")
                    
                    with col2:
                        st.write(str(field.value) if field.value is not None else 'Not Found')
                    
                    with col3:
                        confidence_class = get_confidence_class(field.confidence)
                        st.markdown(f'<span class="{confidence_class}">{field.confidence:.1%}</span>', 
                                   unsafe_allow_html=True)
                
                # Download JSON
                extracted_data = {field.name: {"value": field.value, "confidence": field.confidence} for field in fields}
                json_data = json.dumps(extracted_data, indent=2, default=str)
                st.download_button(
                    label="📥 Download JSON",
                    data=json_data,
                    file_name=f"extracted_data_{doc_type}.json",
                    mime="application/json"
                )
            else:
                st.warning("No data extracted from the document")
            
            # Validation results
            if qa_results and qa_results.failed_rules:
                st.subheader("🔍 Validation Issues")
                for rule in qa_results.failed_rules:
                    st.error(f"• {rule}")
            
            # Debug information
            if show_debug:
                st.subheader("🐛 Debug Information")
                with st.expander("Raw Processing Result"):
                    st.json(result.__dict__ if hasattr(result, '__dict__') else str(result))
                    
        except Exception as e:
            st.error(f"Error displaying results: {str(e)}")
            if show_debug:
                st.code(traceback.format_exc())

def get_confidence_class(confidence: float) -> str:
    """Get CSS class based on confidence level"""
    if confidence >= 0.8:
        return "confidence-high"
    elif confidence >= 0.6:
        return "confidence-medium"
    else:
        return "confidence-low"

if __name__ == "__main__":
    main()
