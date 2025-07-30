#!/bin/bash

# Google Cloud Run Deployment Script
# Make sure you have gcloud CLI installed and authenticated

set -e

# Configuration
PROJECT_ID=""  # Set this to your GCP project ID
REGION="us-central1"
SERVICE_NAME="cover-letter-api"

# Security: Don't put secrets in this file!
# OpenAI API key will be prompted or read from environment

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Cover Letter API - Google Cloud Run Deployment${NC}"
echo "=================================================="

# Get PROJECT_ID if not set
if [ -z "$PROJECT_ID" ]; then
    # Try to get from gcloud config
    PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
    
    if [ -z "$PROJECT_ID" ]; then
        echo -e "${YELLOW}No PROJECT_ID found. Please enter your GCP project ID:${NC}"
        read -p "Project ID: " PROJECT_ID
        
        if [ -z "$PROJECT_ID" ]; then
            echo -e "${RED}❌ PROJECT_ID is required${NC}"
            exit 1
        fi
    fi
fi

# Get OpenAI API key securely
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}🔐 Enter your OpenAI API key (input will be hidden):${NC}"
    read -s -p "OpenAI API Key: " OPENAI_API_KEY
    echo  # New line after hidden input
    
    if [ -z "$OPENAI_API_KEY" ]; then
        echo -e "${RED}❌ OpenAI API key is required${NC}"
        exit 1
    fi
    
    # Basic validation - OpenAI keys start with 'sk-'
    if [[ ! "$OPENAI_API_KEY" =~ ^sk- ]]; then
        echo -e "${RED}❌ Invalid OpenAI API key format (should start with 'sk-')${NC}"
        exit 1
    fi
fi

echo -e "${GREEN}✓ Using Project ID: $PROJECT_ID${NC}"
echo -e "${GREEN}✓ Using Region: $REGION${NC}"
echo -e "${GREEN}✓ Service Name: $SERVICE_NAME${NC}"
echo ""

# Enable required APIs
echo -e "${YELLOW}📋 Enabling required Google Cloud APIs...${NC}"
gcloud services enable cloudbuild.googleapis.com --project=$PROJECT_ID
gcloud services enable run.googleapis.com --project=$PROJECT_ID
gcloud services enable containerregistry.googleapis.com --project=$PROJECT_ID

# Build and submit to Cloud Build
echo -e "${YELLOW}🔨 Building container image...${NC}"
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME --project=$PROJECT_ID

# Deploy to Cloud Run
echo -e "${YELLOW}🚀 Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "OPENAI_API_KEY=$OPENAI_API_KEY" \
  --project=$PROJECT_ID

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --platform managed --region $REGION --format 'value(status.url)' --project=$PROJECT_ID)

echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo "=================================================="
echo -e "${GREEN}✅ Service URL: $SERVICE_URL${NC}"
echo -e "${GREEN}✅ API Documentation: $SERVICE_URL/docs${NC}"
echo -e "${GREEN}✅ Health Check: $SERVICE_URL/${NC}"
echo ""
echo -e "${YELLOW}💡 Next steps:${NC}"
echo "1. Update your frontend to use the new API URL"
echo "2. Test the endpoints at $SERVICE_URL/docs"
echo "3. Monitor usage in Google Cloud Console"
echo ""
echo -e "${YELLOW}💰 Cost optimization tips:${NC}"
echo "- Cloud Run scales to zero when not used (no cost)"
echo "- You're billed only for actual requests"
echo "- Monitor OpenAI API usage to control costs"
echo ""
echo -e "${YELLOW}🔒 For automated deployments, set environment variables:${NC}"
echo "export PROJECT_ID=your-project-id"
echo "export OPENAI_API_KEY=sk-your-key-here"
echo "Then run: ./deploy-gcp.sh" 