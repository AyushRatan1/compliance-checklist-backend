import json
import os
import boto3
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def handler(request):
    """Vercel serverless function handler for health check"""
    
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
        # Check AWS configuration
        aws_configured = bool(
            os.getenv('AWS_ACCESS_KEY_ID') and 
            os.getenv('AWS_SECRET_ACCESS_KEY')
        )
        
        # Test AWS connection if configured
        aws_connection_ok = False
        if aws_configured:
            try:
                test_client = boto3.client(
                    'sts',
                    region_name=os.getenv('AWS_REGION', 'us-east-1'),
                    aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
                )
                test_client.get_caller_identity()
                aws_connection_ok = True
            except Exception as e:
                logger.error(f"AWS connection test failed: {e}")
        
        response_data = {
            "status": "healthy",
            "version": "2.0.0",
            "services": {
                "aws_configured": aws_configured,
                "aws_connection": aws_connection_ok
            },
            "timestamp": "2024-01-01T00:00:00Z"
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
        logger.error(f"Health check failed: {e}")
        
        error_response = {
            "status": "unhealthy",
            "error": str(e)
        }
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
            },
            'body': json.dumps(error_response)
        } 