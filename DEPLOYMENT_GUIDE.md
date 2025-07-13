# Vercel Deployment Guide

## Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **GitHub Integration**: Connect your GitHub repository to Vercel
3. **AWS Account**: Required for AWS Bedrock Claude API (optional - fallback available)

## Deployment Steps

### 1. Connect Repository to Vercel

1. Log in to your Vercel dashboard
2. Click "New Project"
3. Import your GitHub repository
4. Select `compliance-checklist-app` as the root directory

### 2. Configure Build Settings

Vercel will automatically detect the configuration from `vercel.json`. No manual configuration needed.

**Project Settings:**
- **Framework Preset**: Other
- **Build Command**: Automatically detected from `vercel.json`
- **Output Directory**: Automatically detected from `vercel.json`
- **Install Command**: `npm install` (for frontend)

### 3. Environment Variables

Add these environment variables in your Vercel project settings:

#### Required for AWS Bedrock (Optional)
```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

#### Optional Environment Variables
```
ENVIRONMENT=production
BING_API_KEY=your_bing_api_key (optional for web search)
MAX_CONTENT_CHARS=10000000
CHUNK_SIZE_CHARS=400000
```

### 4. Deploy

1. Click "Deploy" in Vercel
2. Wait for the build to complete
3. Your app will be available at `https://your-project-name.vercel.app`

## Project Structure

```
compliance-checklist-app/
├── vercel.json              # Vercel configuration
├── api/                     # Serverless API functions
│   ├── generate-checklist.py
│   ├── health.py
│   ├── supported-formats.py
│   └── requirements.txt
├── frontend/                # React frontend
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── DEPLOYMENT_GUIDE.md
```

## API Endpoints

After deployment, your API will be available at:

- **Health Check**: `https://your-app.vercel.app/api/health`
- **Generate Checklist**: `https://your-app.vercel.app/api/generate-checklist`
- **Supported Formats**: `https://your-app.vercel.app/api/supported-formats`

## Frontend Configuration

The frontend automatically detects the environment and configures API URLs:

- **Development**: `http://localhost:8002`
- **Production**: `/api` (relative to your Vercel domain)

## AWS Configuration (Optional)

### Setting up AWS Bedrock

1. **Create AWS Account**: Go to [aws.amazon.com](https://aws.amazon.com)
2. **Enable Bedrock**: Navigate to AWS Bedrock console
3. **Request Model Access**: Request access to Claude 3 Sonnet model
4. **Create IAM User**: Create IAM user with Bedrock permissions
5. **Get Credentials**: Generate access key and secret key

### IAM Policy for Bedrock Access

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "bedrock:InvokeModel",
                "bedrock:ListFoundationModels"
            ],
            "Resource": "*"
        }
    ]
}
```

## Troubleshooting

### Common Issues

1. **Build Fails**: Check that `frontend/package.json` has `build-static` script
2. **API Not Working**: Verify environment variables are set correctly
3. **AWS Issues**: Ensure Bedrock model access is approved (can take 24-48 hours)

### Fallback Mode

If AWS is not configured, the app will work in fallback mode with:
- Pre-defined compliance checklists
- Basic functionality without AI generation
- All other features remain functional

### Logs and Debugging

1. Check Vercel function logs in the dashboard
2. Monitor API responses from the frontend
3. Use browser developer tools for client-side debugging

### Performance Optimization

1. **Cold Start**: First API call may take 5-10 seconds
2. **Caching**: Responses are not cached by default
3. **Timeout**: API functions have 300-second timeout

## Features

- **AI-Powered**: Uses Claude 3 Sonnet for intelligent checklist generation
- **Multiple Formats**: Supports PDF, DOCX, TXT, MD files
- **Web Scraping**: Extracts content from URLs
- **Industry-Specific**: Tailored for different industries and frameworks
- **Export Options**: JSON and CSV download
- **Responsive Design**: Works on desktop and mobile
- **Serverless**: Uses Vercel's Python runtime for scalable deployment

## Support

For issues or questions:
1. Check the Vercel deployment logs
2. Review the API health endpoint
3. Verify environment variables are set correctly
4. Ensure all dependencies are in `requirements.txt`

## Security Notes

- API keys are stored as environment variables
- CORS is configured for public access
- File uploads are limited to supported formats
- Content processing has size limits for performance 