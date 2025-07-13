import json
import os
import boto3
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
from botocore.config import Config
import uuid
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

def extract_text_from_file(file_content: bytes, filename: str) -> str:
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

def fetch_url_content(url: str) -> str:
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

def handler(request):
    """Vercel serverless function handler"""
    
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        }
    
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': 'Method not allowed'})
        }
    
    try:
        # Parse request body
        request_data = json.loads(request.body)
        
        request_id = str(uuid.uuid4())
        logger.info(f"Processing request {request_id}")
        
        # Process all content
        all_content = []
        
        # Process URLs
        for url in request_data.get('primary_references', []):
            if url.startswith('http'):
                content = fetch_url_content(url)
                if content:
                    all_content.append(content)
            else:
                all_content.append(url)
        
        # Process uploaded files
        if request_data.get('uploaded_files') and request_data.get('file_names'):
            for file_content, filename in zip(request_data['uploaded_files'], request_data['file_names']):
                try:
                    file_bytes = base64.b64decode(file_content)
                    text = extract_text_from_file(file_bytes, filename)
                    if text:
                        all_content.append(text)
                except Exception as e:
                    logger.error(f"Error processing file {filename}: {e}")
        
        # Combine all content
        combined_content = "\n\n".join(all_content)
        
        # Create context
        context = {
            'industry': request_data.get('industry'),
            'jurisdiction': request_data.get('jurisdiction'),
            'compliance_framework': request_data.get('compliance_framework'),
            'audience': request_data.get('audience', 'Compliance'),
            'detail_level': request_data.get('detail_level', 'comprehensive'),
            'context_scope_hints': request_data.get('context_scope_hints')
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
        
        # Create response
        response_data = {
            'checklists': checklists,
            'metadata': {
                'request_id': request_id,
                'items_generated': len(checklists),
                'aws_configured': aws_configured
            }
        }
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps({'error': str(e)})
        } 