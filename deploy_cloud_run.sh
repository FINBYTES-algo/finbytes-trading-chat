#!/bin/bash
set -e

export GCP_PROJECT_ID=ohlcdata
export REGION=us-central1
export SERVICE_NAME=finbytes-api

echo "🚀 Deploying FinBytes API to Google Cloud Run"
echo "Project: $GCP_PROJECT_ID"
echo "Region: $REGION"
echo ""

# Set project
gcloud config set project $GCP_PROJECT_ID

# Enable APIs
echo "📋 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# Build image
echo "🔨 Building Docker image..."
gcloud builds submit --tag gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo "☁️  Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME \
  --image gcr.io/$GCP_PROJECT_ID/$SERVICE_NAME \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0 \
  --set-env-vars="PYTHONUNBUFFERED=1"

# Get service URL
API_URL=$(gcloud run services describe $SERVICE_NAME \
  --region $REGION \
  --format 'value(status.url)')

echo ""
echo "✅ Deployment complete!"
echo "🌐 API URL: ${API_URL}"
echo "📝 Health check: ${API_URL}/health"
echo "📝 Analysis endpoint: ${API_URL}/analyze"
echo ""
echo "Use this URL in Streamlit Cloud environment variable:"
echo "API_URL=${API_URL}/analyze"
