# Professional Compliance Checklist Generator - Backend v2.0

## Overview

Enterprise-grade compliance checklist generation using AWS Bedrock Claude. This backend service converts regulatory documents, standards, and policies into detailed, actionable compliance checklists.

## Features

- **AWS Bedrock Claude Integration**: Uses advanced AI for accurate compliance interpretation
- **Multi-format Document Support**: PDF, DOCX, TXT, MD files
- **Enhanced URL Processing**: Intelligent content extraction from regulatory websites
- **Industry-specific Generation**: Tailored outputs for different sectors and jurisdictions
- **Priority & Frequency Analysis**: Automatic classification of checklist items
- **Professional API Documentation**: Full OpenAPI/Swagger integration

## Setup

### Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- AWS CLI configured or IAM user with Bedrock permissions

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure AWS credentials (choose one method):

   **Option A: Environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your AWS credentials
   ```

   **Option B: AWS CLI**
   ```bash
   aws configure
   ```

   **Option C: IAM Roles** (recommended for production)

3. Start the server:
```bash
python main.py
```

## Environment Variables

```bash
AWS_ACCESS_KEY_ID=your_aws_access_key_here
AWS_SECRET_ACCESS_KEY=your_aws_secret_key_here
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
PORT=8000
```

## API Endpoints

### Core Endpoints

- `POST /generate-checklist` - Generate compliance checklists
- `POST /upload-and-analyze` - Direct file upload and analysis
- `GET /health` - Health check with AWS status
- `GET /supported-formats` - Available formats and options
- `GET /` - API information

### Interactive Documentation

Visit `http://localhost:8000/docs` for full API documentation with examples.

## Example Request

```json
{
  "primary_references": [
    "https://example.com/regulation.pdf",
    "Direct text of compliance requirements..."
  ],
  "uploaded_files": ["base64_encoded_file_content"],
  "file_names": ["regulation.pdf"],
  "context_scope_hints": "Focus on data privacy controls",
  "industry": "Banking & Financial Services",
  "jurisdiction": "United States",
  "compliance_framework": "SOC 2",
  "audience": "Compliance",
  "detail_level": "comprehensive"
}
```

## Example Response

```json
{
  "checklists": [
    {
      "checklist_name": "Data Encryption Controls",
      "checklist_category": "Data Protection & Privacy",
      "checklist_ai_description": "1. Verify AES-256 encryption implemented for data at rest with documented key rotation every 90 days. 2. Confirm TLS 1.3 minimum for data in transit with certificate validation. 3. Test encryption key management system access controls and backup procedures.",
      "priority": "critical",
      "frequency": "Quarterly"
    }
  ],
  "metadata": {
    "total_checklists": 12,
    "categories": ["Data Protection & Privacy", "Access Control"],
    "generation_context": {
      "industry": "Banking & Financial Services",
      "jurisdiction": "United States"
    }
  }
}
```

## Supported Industries

- Banking & Financial Services
- Healthcare
- Insurance
- Technology
- Manufacturing
- Retail
- Government
- Energy & Utilities

## Supported Jurisdictions

- United States
- European Union
- United Kingdom
- India
- Singapore
- Australia
- Canada

## Supported Frameworks

- SOC 2
- ISO 27001
- HIPAA
- GDPR
- PCI-DSS
- NIST
- CIS
- COBIT
- Basel III
- Solvency II

## AWS Bedrock Setup

1. **Enable Bedrock Access**: Ensure your AWS account has access to Bedrock
2. **Model Access**: Request access to Claude models in your AWS region
3. **IAM Permissions**: Grant necessary permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": "arn:aws:bedrock:*::foundation-model/anthropic.claude-*"
    }
  ]
}
```

## Troubleshooting

### Common Issues

1. **AWS Credentials**: Ensure proper AWS configuration
2. **Model Access**: Verify Bedrock model access in your region
3. **Large Files**: Increase timeout for processing large documents
4. **Memory**: Monitor memory usage for extensive document processing

### Error Codes

- `400`: Invalid input or missing references
- `500`: AWS Bedrock integration errors
- `503`: Service temporarily unavailable

## Performance

- **Typical Response Time**: 5-15 seconds for comprehensive checklists
- **Document Limits**: Up to 10MB per file, 20,000 characters per URL
- **Concurrent Requests**: Supports multiple simultaneous requests

## Development

Run in development mode:
```bash
uvicorn main:app --reload --port 8000
```

## License

MIT License 