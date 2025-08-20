# Agentic Document Extraction System

An intelligent document processing system that uses AI agents to extract structured data from invoices, medical bills, and prescriptions with confidence scoring and validation.

## 🚀 Features

- **Multi-Agent Architecture**: Specialized agents for routing, OCR, extraction, and validation
- **Document Type Detection**: Automatically identifies invoices, medical bills, and prescriptions
- **Structured Data Extraction**: Extracts key-value pairs with confidence scores
- **Quality Assurance**: Cross-field validation and rule-based checks
- **Interactive UI**: Streamlit-based web interface with real-time processing
- **Confidence Scoring**: Multi-factor confidence calculation for reliability
- **Robust Processing**: Error handling, retries, and graceful degradation

## 🏗️ Architecture

### Agent Pipeline
1. **Document Router**: Detects document type using GPT-4 Vision
2. **OCR Processor**: Extracts text with bounding boxes using Tesseract
3. **Extraction Agent**: Structured data extraction using LLM with schema validation
4. **Validation Agent**: Quality assurance with cross-field validation rules

### Confidence Scoring
Multi-factor confidence calculation based on:
- LLM extraction confidence
- OCR text confidence
- Field format validation
- Document type relevance
- Cross-field consistency

## 📋 Requirements

- Python 3.8+
- OpenAI API key
- Tesseract OCR (for text extraction)

## 🛠️ Installation

1. **Clone the repository:**
\`\`\`bash
git clone <repository-url>
cd agentic-document-extraction
\`\`\`

2. **Install dependencies:**
\`\`\`bash
pip install -r requirements.txt
\`\`\`

3. **Install Tesseract OCR:**

**Ubuntu/Debian:**
\`\`\`bash
sudo apt-get install tesseract-ocr
\`\`\`

**macOS:**
\`\`\`bash
brew install tesseract
\`\`\`

**Windows:**
Download from: https://github.com/UB-Mannheim/tesseract/wiki

4. **Set up environment variables (optional):**
\`\`\`bash
cp .env.example .env
# Edit .env with your OpenAI API key
\`\`\`

## 🚀 Usage

### Run the Streamlit App

\`\`\`bash
streamlit run app.py
\`\`\`

### Using the Interface

1. **Enter API Key**: Add your OpenAI API key in the sidebar
2. **Upload Document**: Choose a PDF or image file (invoices, medical bills, prescriptions)
3. **Custom Fields** (Optional): Specify additional fields to extract
4. **Process**: Click "Process Document" to start extraction
5. **Review Results**: View extracted fields, confidence scores, and validation results
6. **Download**: Export results as JSON

### Supported Document Types

- **Invoices**: Invoice number, vendor info, line items, totals
- **Medical Bills**: Patient info, provider details, charges, insurance
- **Prescriptions**: Patient name, medications, dosage, prescriber info

## 📊 Output Format

\`\`\`json
{
  "doc_type": "invoice|medical_bill|prescription",
  "fields": [
    {
      "name": "patient_name",
      "value": "John Doe",
      "confidence": 0.95,
      "source": {
        "page": 1,
        "bbox": {"x1": 100, "y1": 200, "x2": 300, "y2": 220},
        "ocr_confidence": 0.92
      },
      "validation_passed": true,
      "validation_notes": "Valid"
    }
  ],
  "overall_confidence": 0.88,
  "qa": {
    "passed_rules": ["totals_match", "required_fields"],
    "failed_rules": [],
    "notes": "All validations passed",
    "cross_validation_score": 0.95
  },
  "processing_time": 3.45,
  "metadata": {
    "filename": "invoice.pdf",
    "num_pages": 1
  }
}
\`\`\`

## 🔧 Configuration

Key settings in `src/config.py`:

- **OpenAI Models**: GPT-4 Vision for extraction, GPT-4 Turbo for text processing
- **Confidence Thresholds**: Minimum field (0.5) and overall (0.7) confidence
- **Validation Rules**: Regex patterns for email, phone, date, amount validation
- **OCR Settings**: Tesseract configuration for optimal text extraction

## 🧪 Testing

The system includes comprehensive validation:

- **Format Validation**: Email, phone, date, amount format checks
- **Cross-Field Validation**: Invoice totals, medical bill balances
- **Confidence Thresholds**: Configurable minimum confidence levels
- **Error Handling**: Graceful degradation with informative error messages

## 🎯 Confidence Scoring Methodology

The confidence scoring system uses a weighted combination of multiple factors:

1. **LLM Confidence (40%)**: Model's confidence in extraction accuracy
2. **OCR Confidence (30%)**: Text recognition quality from Tesseract
3. **Format Validation (20%)**: Field format compliance (email, date, etc.)
4. **Document Relevance (10%)**: Field relevance to detected document type

### Cross-Validation Score
Additional validation through:
- Mathematical consistency (invoice totals, medical bill balances)
- Required field presence
- Format compliance across related fields

## 📁 Project Structure

\`\`\`
agentic-document-extraction/
├── src/
│   ├── agents/
│   │   ├── document_router.py      # Document type detection
│   │   ├── ocr_processor.py        # OCR and text extraction
│   │   ├── extraction_agent.py     # LLM-based data extraction
│   │   └── validation_agent.py     # Quality assurance
│   ├── core/
│   │   └── document_processor.py   # Main processing orchestrator
│   ├── models/
│   │   └── document_models.py      # Pydantic data models
│   ├── ui/
│   │   └── streamlit_app.py        # Streamlit interface
│   └── config.py                   # Configuration settings
├── app.py                          # Application entry point
├── requirements.txt                # Python dependencies
└── README.md                       # This file
\`\`\`

## 🔒 Security

- API keys are handled securely through environment variables
- No sensitive data is logged or stored permanently
- Input validation prevents malicious file uploads
- Rate limiting and timeout protection included

## 🚀 Deployment

### Local Development
\`\`\`bash
streamlit run app.py
\`\`\`

### Production Deployment
The app can be deployed to:
- Streamlit Cloud
- Heroku
- AWS/GCP/Azure
- Docker containers

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the GitHub Issues page
2. Review the troubleshooting section below
3. Create a new issue with detailed information

## 🔧 Troubleshooting

### Common Issues

**Tesseract not found:**
- Ensure Tesseract is installed and in your PATH
- On Windows, add Tesseract installation directory to PATH

**OpenAI API errors:**
- Verify API key is correct and has sufficient credits
- Check rate limits and quotas

**Low extraction confidence:**
- Ensure document image is clear and high resolution
- Try preprocessing the image for better contrast
- Verify document type is supported

**Memory issues with large PDFs:**
- Reduce PDF resolution in `pdf2image.convert_from_bytes()`
- Process single pages instead of entire documents
