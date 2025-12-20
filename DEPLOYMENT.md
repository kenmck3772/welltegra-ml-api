# Deployment Guide

Complete guide for deploying WellTegra ML API to Google Cloud Platform.

## Prerequisites

- Google Cloud SDK installed: `gcloud --version`
- Authenticated: `gcloud auth login`
- Project set: `gcloud config set project portfolio-project-481815`
- BigQuery data uploaded (see welltegra.network/scripts/upload-to-bigquery.py)

## Option 1: Deploy to Cloud Functions (Recommended)

**Best for:** Serverless, auto-scaling API with minimal management

### Step 1: Enable APIs

```bash
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable bigquery.googleapis.com
```

### Step 2: Deploy Function

```bash
gcloud functions deploy welltegra-api \
  --gen2 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point api \
  --region us-central1 \
  --memory 512MB \
  --timeout 60s \
  --set-env-vars GCP_PROJECT_ID=portfolio-project-481815,BIGQUERY_DATASET=welltegra_historical
```

### Step 3: Get Function URL

```bash
gcloud functions describe welltegra-api --region us-central1 --format='value(serviceConfig.uri)'
```

### Step 4: Test Deployment

```bash
FUNCTION_URL=$(gcloud functions describe welltegra-api --region us-central1 --format='value(serviceConfig.uri)')
curl $FUNCTION_URL/api/v1/health
```

## Option 2: Deploy to Cloud Run

**Best for:** More control, Docker-based deployment, custom scaling

### Step 1: Build Container

```bash
# Build with Cloud Build
gcloud builds submit --tag gcr.io/portfolio-project-481815/welltegra-api

# Or build locally (requires Docker)
docker build -t gcr.io/portfolio-project-481815/welltegra-api .
docker push gcr.io/portfolio-project-481815/welltegra-api
```

### Step 2: Deploy to Cloud Run

```bash
gcloud run deploy welltegra-api \
  --image gcr.io/portfolio-project-481815/welltegra-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GCP_PROJECT_ID=portfolio-project-481815,BIGQUERY_DATASET=welltegra_historical \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10
```

### Step 3: Get Service URL

```bash
gcloud run services describe welltegra-api --region us-central1 --format='value(status.url)'
```

## Option 3: Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GCP_PROJECT_ID=portfolio-project-481815
export BIGQUERY_DATASET=welltegra_historical
export FLASK_ENV=development

# Run locally
python main.py

# API available at: http://localhost:8080
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GCP_PROJECT_ID` | Yes | `portfolio-project-481815` | Google Cloud Project ID |
| `BIGQUERY_DATASET` | Yes | `welltegra_historical` | BigQuery dataset name |
| `FLASK_ENV` | No | `development` | Environment (development/production) |
| `PORT` | No | `8080` | Port for local development |
| `LOG_LEVEL` | No | `INFO` | Logging level |

## Testing Deployment

### Health Check

```bash
curl https://YOUR-FUNCTION-URL/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "bigquery": "connected",
  "runs_count": 3
}
```

### Get All Runs

```bash
curl https://YOUR-FUNCTION-URL/api/v1/runs
```

### Get Specific Run

```bash
curl https://YOUR-FUNCTION-URL/api/v1/runs/byford-r16
```

### Get Tool Statistics

```bash
curl https://YOUR-FUNCTION-URL/api/v1/tools?category=fishing
```

## Monitoring & Logs

### View Logs (Cloud Functions)

```bash
gcloud functions logs read welltegra-api --region us-central1 --limit 50
```

### View Logs (Cloud Run)

```bash
gcloud run services logs read welltegra-api --region us-central1 --limit 50
```

### Cloud Console

- Functions: https://console.cloud.google.com/functions
- Cloud Run: https://console.cloud.google.com/run
- Logs: https://console.cloud.google.com/logs

## Update Deployment

### Redeploy Cloud Function

```bash
gcloud functions deploy welltegra-api \
  --gen2 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point api \
  --region us-central1
```

### Redeploy Cloud Run

```bash
gcloud builds submit --tag gcr.io/portfolio-project-481815/welltegra-api
gcloud run deploy welltegra-api \
  --image gcr.io/portfolio-project-481815/welltegra-api \
  --region us-central1
```

## CI/CD with GitHub Actions

Automatic deployment on push to main branch:

```yaml
# See .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: google-github-actions/setup-gcloud@v1
      - run: gcloud functions deploy welltegra-api ...
```

## Security

### Add Authentication

```bash
# Remove --allow-unauthenticated
# Require authentication
gcloud functions deploy welltegra-api \
  --gen2 \
  --runtime python311 \
  --trigger-http \
  --entry-point api \
  --region us-central1
```

### API Key (Future)

```python
# Add to main.py
@app.before_request
def check_api_key():
    api_key = request.headers.get('X-API-Key')
    if api_key != os.getenv('API_KEY'):
        return jsonify({'error': 'Invalid API key'}), 401
```

## Costs

**Free Tier Limits:**
- Cloud Functions: 2M invocations/month
- Cloud Run: 2M requests/month
- BigQuery: 1 TB queries/month

**Estimated Monthly Cost:**
- Within free tier: $0
- Light production use: $1-10/month
- Heavy use: $20-50/month

## Troubleshooting

### Error: "Permission denied"

```bash
# Ensure service account has BigQuery Data Viewer role
gcloud projects add-iam-policy-binding portfolio-project-481815 \
  --member=serviceAccount:YOUR-SA@portfolio-project-481815.iam.gserviceaccount.com \
  --role=roles/bigquery.dataViewer
```

### Error: "BigQuery table not found"

```bash
# Upload data first
cd ../welltegra.network
python3 scripts/upload-to-bigquery.py
```

### Error: "Module not found"

```bash
# Check requirements.txt is complete
# Redeploy with --clear-env-vars flag
gcloud functions deploy welltegra-api --clear-env-vars ...
```

## Delete Deployment

### Delete Cloud Function

```bash
gcloud functions delete welltegra-api --region us-central1
```

### Delete Cloud Run Service

```bash
gcloud run services delete welltegra-api --region us-central1
```

## Next Steps

1. ✅ Deploy to Cloud Functions
2. ⬜ Add authentication
3. ⬜ Integrate with Vertex AI for predictions
4. ⬜ Add caching layer (Memorystore)
5. ⬜ Set up monitoring alerts
6. ⬜ Create Looker dashboard
7. ⬜ Add rate limiting
