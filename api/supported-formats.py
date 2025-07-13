import json

def handler(request):
    """Vercel serverless function handler for supported formats"""
    
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type',
            }
        }
    
    try:
        response_data = {
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
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        error_response = {"error": str(e)}
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(error_response)
        } 