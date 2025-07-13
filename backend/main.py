from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import boto3
import json
import os
import requests
from bs4 import BeautifulSoup
import re
import PyPDF2
import docx
import chardet
import markdown
from io import BytesIO
import base64
import logging
import sys
from botocore.config import Config
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Compliance Checklist Generator API",
    description="AI-powered compliance checklist generation using AWS Bedrock Claude",
    version="2.0.0"
)

# Configure CORS - Allow all origins for now
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your Vercel domain
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request and Response models
class ComplianceRequest(BaseModel):
    primary_references: List[str] = Field(..., description="URLs or text of governing rule sets")
    uploaded_files: Optional[List[str]] = Field(None, description="Base64 encoded files")
    file_names: Optional[List[str]] = Field(None, description="Names of uploaded files")
    context_scope_hints: Optional[str] = Field(None, description="Additional context or scope hints")
    industry: Optional[str] = Field(None, description="Industry vertical")
    jurisdiction: Optional[str] = Field(None, description="Regulatory jurisdiction")
    compliance_framework: Optional[str] = Field(None, description="Specific compliance framework")
    audience: Optional[str] = Field("Compliance", description="Target audience for the checklist")
    detail_level: Optional[str] = Field("comprehensive", description="Level of detail: basic, standard, comprehensive")

class ChecklistItem(BaseModel):
    checklist_name: str
    checklist_category: str
    checklist_ai_description: str
    scheduled_runs: str = Field(..., description="Cron expression for scheduled execution")

class ComplianceResponse(BaseModel):
    checklists: List[ChecklistItem]
    metadata: Dict[str, Any] = Field(default_factory=dict)

# Initialize AWS Bedrock client
bedrock_runtime = None
aws_configured = False

try:
    if os.getenv('AWS_ACCESS_KEY_ID') and os.getenv('AWS_SECRET_ACCESS_KEY'):
        bedrock_runtime = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.getenv('AWS_REGION', 'us-east-1'),
            aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
            config=Config(
                read_timeout=300,
                connect_timeout=30,
                retries={"max_attempts": 3}
            )
        )
        aws_configured = True
        logger.info("AWS Bedrock client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Bedrock client: {e}")
    aws_configured = False

# Utility functions
async def extract_text_from_file(file_content: bytes, filename: str) -> str:
    """Extract text from uploaded file based on its type"""
    try:
        if filename.lower().endswith('.pdf'):
            pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
        elif filename.lower().endswith('.docx'):
            doc = docx.Document(BytesIO(file_content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        elif filename.lower().endswith(('.txt', '.md')):
            encoding = chardet.detect(file_content)['encoding'] or 'utf-8'
            text = file_content.decode(encoding)
            if filename.lower().endswith('.md'):
                text = markdown.markdown(text)
            return text
        else:
            return ""
    except Exception as e:
        logger.error(f"Error extracting text from file {filename}: {e}")
        return ""

async def fetch_url_content(url: str) -> str:
    """Fetch and extract content from URL"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:50000]  # Limit to first 50k characters
    except Exception as e:
        logger.error(f"Error fetching URL {url}: {e}")
        return ""

def generate_checklist_with_bedrock(content: str, context: Dict[str, Any]) -> List[Dict]:
    """Generate checklist using AWS Bedrock"""
    try:
        system_prompt = """You are an elite regulatory compliance expert with 20+ years of experience. Convert regulatory documents into comprehensive, actionable compliance checklists.

CRITICAL: You MUST respond with ONLY valid JSON in the exact format specified. NO other text, explanations, or formatting.

Generate 10-20 comprehensive checklist items covering all major compliance areas. Each checklist item must be complete with numbered steps and specific criteria."""

        prompt = f"""
        {system_prompt}

        Industry: {context.get('industry', 'General')}
        Jurisdiction: {context.get('jurisdiction', 'General')}
        Framework: {context.get('compliance_framework', 'General')}
        Audience: {context.get('audience', 'Compliance')}
        Detail Level: {context.get('detail_level', 'comprehensive')}

        Content to analyze:
        {content[:30000]}

        Generate JSON response with this exact structure:
        {{
            "checklists": [
                {{
                    "checklist_name": "Clear, specific checklist name",
                    "checklist_category": "Category (e.g., Data Protection, Financial Reporting, etc.)",
                    "checklist_ai_description": "Detailed description with numbered steps:\\n1. Step one\\n2. Step two\\n3. Step three",
                    "scheduled_runs": "0 0 * * *"
                }}
            ]
        }}
        """

        response = bedrock_runtime.invoke_model(
            modelId="anthropic.claude-3-sonnet-20240229-v1:0",
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "temperature": 0.3,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }),
            contentType="application/json"
        )
        
        response_body = json.loads(response['body'].read())
        generated_text = response_body['content'][0]['text']
        
        json_match = re.search(r'\{.*\}', generated_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()
            result = json.loads(json_str)
            return result.get('checklists', [])
        else:
            logger.error("No JSON found in Bedrock response")
            return []
            
    except Exception as e:
        logger.error(f"Error generating checklist with Bedrock: {e}")
        return []

def create_fallback_checklist(content: str, context: Dict[str, Any]) -> List[Dict]:
    """Create fallback checklist when Bedrock is not available"""
    industry = context.get('industry', 'General')
    framework = context.get('compliance_framework', 'General')
    
    return [
        {
            "checklist_name": f"{industry} Data Protection Compliance Review",
            "checklist_category": "Data Protection",
            "checklist_ai_description": "1. Review data collection practices and ensure explicit consent is obtained\n2. Verify data storage security measures including encryption at rest and in transit\n3. Audit data retention policies and implement automated deletion procedures\n4. Validate data subject rights implementation (access, rectification, deletion)\n5. Check cross-border data transfer compliance and adequacy decisions",
            "scheduled_runs": "0 0 * * 1"
        },
        {
            "checklist_name": f"{framework} Security Assessment",
            "checklist_category": "Security",
            "checklist_ai_description": "1. Conduct comprehensive vulnerability scans and penetration testing\n2. Review access controls and implement least privilege principles\n3. Test incident response procedures and business continuity plans\n4. Validate backup and recovery systems with regular restore tests\n5. Check security monitoring logs and SIEM alert configurations",
            "scheduled_runs": "0 0 * * *"
        },
        {
            "checklist_name": f"{industry} Financial Controls Review",
            "checklist_category": "Financial Reporting",
            "checklist_ai_description": "1. Verify segregation of duties in financial processes\n2. Review approval workflows and authorization limits\n3. Audit reconciliation procedures and variance analysis\n4. Check internal controls testing and documentation\n5. Validate financial reporting accuracy and completeness",
            "scheduled_runs": "0 0 1 * *"
        }
    ]

# API Routes
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Compliance Checklist Generator API", "version": "2.0.0", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        aws_configured_status = bool(
            os.getenv('AWS_ACCESS_KEY_ID') and 
            os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        return {
            "status": "healthy",
            "version": "2.0.0",
            "services": {
                "aws_configured": aws_configured_status,
                "aws_connection": aws_configured
            },
            "environment": os.getenv('RAILWAY_ENVIRONMENT', 'development')
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/supported-formats")
async def supported_formats():
    """Get supported file formats and input types"""
    return {
        "supported_formats": {
            "files": [
                {"extension": ".pdf", "description": "PDF documents"},
                {"extension": ".docx", "description": "Microsoft Word documents"},
                {"extension": ".txt", "description": "Plain text files"},
                {"extension": ".md", "description": "Markdown files"}
            ],
            "urls": [
                {"protocol": "http", "description": "HTTP web pages"},
                {"protocol": "https", "description": "HTTPS web pages"}
            ],
            "text_input": {
                "max_length": 100000,
                "description": "Raw text input for compliance documents"
            }
        },
        "compliance_frameworks": [
            "GDPR",
            "HIPAA",
            "SOX",
            "PCI-DSS",
            "ISO 27001",
            "NIST",
            "CCPA",
            "SOC 2"
        ],
        "industries": [
            "Healthcare",
            "Financial Services",
            "Technology",
            "Retail",
            "Manufacturing",
            "Government",
            "Education",
            "Non-profit"
        ]
    }

@app.post("/generate-checklist", response_model=ComplianceResponse)
async def generate_compliance_checklist(request: ComplianceRequest):
    """Generate compliance checklist from provided references"""
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Processing request {request_id}")
        
        # Process all content
        all_content = []
        
        # Process URLs
        for url in request.primary_references:
            if url.startswith('http'):
                content = await fetch_url_content(url)
                if content:
                    all_content.append(content)
            else:
                all_content.append(url)
        
        # Process uploaded files
        if request.uploaded_files and request.file_names:
            for file_content, filename in zip(request.uploaded_files, request.file_names):
                try:
                    file_bytes = base64.b64decode(file_content)
                    text = await extract_text_from_file(file_bytes, filename)
                    if text:
                        all_content.append(text)
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}")
        
        # Combine all content
        combined_content = "\n\n".join(all_content)
        
        # Create context
        context = {
            'industry': request.industry,
            'jurisdiction': request.jurisdiction,
            'compliance_framework': request.compliance_framework,
            'audience': request.audience,
            'detail_level': request.detail_level,
            'context_scope_hints': request.context_scope_hints
        }
        
        # Generate checklist
        if aws_configured:
            checklists = generate_checklist_with_bedrock(combined_content, context)
        else:
            checklists = create_fallback_checklist(combined_content, context)
        
        # Ensure scheduled_runs is set for all items
        for checklist in checklists:
            if 'scheduled_runs' not in checklist:
                checklist['scheduled_runs'] = "0 0 * * *"
        
        return ComplianceResponse(
            checklists=checklists,
            metadata={
                'request_id': request_id,
                'items_generated': len(checklists),
                'aws_configured': aws_configured
            }
        )
        
    except Exception as e:
        logger.error(f"Error generating checklist: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload-and-analyze")
async def upload_and_analyze(
    files: List[UploadFile] = File(...),
    audience: str = "Compliance",
    industry: Optional[str] = None,
    jurisdiction: Optional[str] = None
):
    """Upload files and analyze for compliance checklist generation"""
    try:
        request_id = str(uuid.uuid4())
        logger.info(f"Processing file upload request {request_id}")
        
        all_content = []
        processed_files = []
        
        for file in files:
            try:
                content = await file.read()
                text = await extract_text_from_file(content, file.filename)
                if text:
                    all_content.append(text)
                    processed_files.append(file.filename)
            except Exception as e:
                logger.error(f"Error processing uploaded file {file.filename}: {e}")
        
        # Combine all content
        combined_content = "\n\n".join(all_content)
        
        # Create context
        context = {
            'industry': industry,
            'jurisdiction': jurisdiction,
            'audience': audience,
            'detail_level': 'comprehensive'
        }
        
        # Generate checklist
        if aws_configured:
            checklists = generate_checklist_with_bedrock(combined_content, context)
        else:
            checklists = create_fallback_checklist(combined_content, context)
        
        return ComplianceResponse(
            checklists=checklists,
            metadata={
                'request_id': request_id,
                'items_generated': len(checklists),
                'processed_files': processed_files,
                'aws_configured': aws_configured
            }
        )
        
    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# For Railway deployment
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port) 