# 🚀 Deploy via Google Cloud Shell (Easiest Method)

## Step 1: Open Cloud Shell

1. In Google Cloud Console, click the **Cloud Shell** icon (terminal icon in top-right)
2. Wait for it to load (it has gcloud pre-installed!)

## Step 2: Upload Your Code

**Option A: Zip Upload**

1. Zip your project folder locally
2. In Cloud Shell, click the "Upload" button
3. Upload your zip file
4. Unzip: `unzip your-project.zip`

**Option B: Git Clone**

1. Push your code to GitHub first
2. In Cloud Shell: `git clone https://github.com/your-username/your-repo.git`

## Step 3: Deploy Commands (Run in Cloud Shell)

```bash
# Navigate to your project
cd your-project-folder

# Set your project (replace with your actual project ID)
gcloud config set project YOUR_PROJECT_ID

# Enable required services
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com

# Build the container
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/cover-letter-api

# Deploy to Cloud Run (replace YOUR_OPENAI_KEY with your actual key)
gcloud run deploy cover-letter-api \
  --image gcr.io/YOUR_PROJECT_ID/cover-letter-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000 \
  --memory 512Mi \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "OPENAI_API_KEY=sk-your-actual-key-here"
```

## Step 4: Get Your URL

After deployment, you'll get a URL like:
`https://cover-letter-api-xxx-uc.a.run.app`

## Step 5: Test

- Health check: Visit your URL
- API docs: Visit `your-url/docs`
