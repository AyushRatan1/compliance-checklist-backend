# Compliance Checklist Generator

A modern, AI-powered compliance checklist generation tool built with React and FastAPI, deployable on Vercel.

## Features

- 🤖 AI-powered checklist generation using AWS Bedrock Claude
- 📄 Document upload and analysis (PDF, DOCX, TXT, MD)
- 🌐 Web scraping for regulatory content
- 🎨 Modern, responsive dashboard interface
- 📊 Export options (JSON, CSV)
- 🔒 Professional compliance focus

## Tech Stack

- **Frontend**: React 18, Vite, React Icons, Axios
- **Backend**: FastAPI, Python 3.9+
- **AI**: AWS Bedrock Claude 3 Sonnet
- **Deployment**: Vercel (Frontend + Serverless Functions)

## Deployment on Vercel

### Prerequisites

1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **AWS Account**: With Bedrock access and Claude 3 Sonnet enabled
3. **Git Repository**: Push your code to GitHub/GitLab/Bitbucket

### Step 1: Environment Variables

In your Vercel dashboard, add these environment variables:

```
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel --prod
```

#### Option B: Using Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "New Project"
3. Import your Git repository
4. Configure:
   - **Framework Preset**: Other
   - **Build Command**: `npm run build`
   - **Output Directory**: `frontend/dist`
   - **Install Command**: `npm run install-frontend`

### Step 3: Environment Variables in Vercel

Add these in your Vercel project settings:

```
AWS_ACCESS_KEY_ID=your_aws_access_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_access_key
AWS_REGION=us-east-1
```

### Step 4: Verify Deployment

1. Visit your Vercel domain
2. Test the API endpoints:
   - `https://yourdomain.vercel.app/api/health`
   - `https://yourdomain.vercel.app/api/supported-formats`

## Local Development

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Backend Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Create .env file
echo "AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1" > .env

# Run FastAPI server
cd backend
uvicorn main:app --reload --port 8002
```

## Project Structure

```
compliance-checklist-app/
├── api/                    # Vercel serverless functions
│   └── main.py            # FastAPI app for Vercel
├── frontend/              # React application
│   ├── src/
│   │   ├── App.jsx        # Main React component
│   │   ├── App.css        # Styling
│   │   └── main.jsx       # React entry point
│   ├── package.json
│   └── vite.config.js
├── backend/               # Local development backend
│   ├── main.py            # Full FastAPI application
│   └── requirements.txt
├── vercel.json            # Vercel configuration
├── requirements.txt       # Python dependencies for Vercel
└── README.md
```

## API Endpoints

- `GET /api/` - API status and health
- `POST /api/generate-checklist` - Generate compliance checklist
- `GET /api/health` - Health check
- `GET /api/supported-formats` - Supported file formats
- `GET /api/progress/{request_id}` - Progress tracking

## Configuration

### AWS Bedrock Setup

1. Enable Claude 3 Sonnet in your AWS Bedrock console
2. Create IAM user with Bedrock permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel",
           "bedrock:GetModel"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

### Frontend Configuration

The frontend automatically detects the environment:
- **Development**: Uses `http://localhost:8002`
- **Production**: Uses `/api` (Vercel serverless functions)

## Troubleshooting

### Common Issues

1. **AWS Credentials Error**
   - Verify environment variables in Vercel dashboard
   - Check AWS region availability for Bedrock

2. **Build Failures**
   - Ensure all dependencies are in `requirements.txt`
   - Check Python version compatibility (3.9+)

3. **API Timeout**
   - Vercel functions have a 60-second timeout
   - Large documents may need processing optimization

### Debug Commands

```bash
# Check Vercel logs
vercel logs

# Test API locally
curl https://yourdomain.vercel.app/api/health

# Test frontend build
cd frontend && npm run build
```

## Performance Optimization

- **Chunked Processing**: Large documents are processed in chunks
- **Caching**: Responses can be cached at the CDN level
- **Compression**: Gzip compression enabled by default
- **Code Splitting**: React components are split for optimal loading

## Security

- **CORS**: Configured for production domains
- **Input Validation**: All inputs are validated and sanitized
- **Rate Limiting**: Can be added via Vercel middleware
- **Environment Variables**: Sensitive data stored securely

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Support

For issues and questions:
- Check the [troubleshooting section](#troubleshooting)
- Open an issue on GitHub
- Check Vercel documentation for deployment issues 