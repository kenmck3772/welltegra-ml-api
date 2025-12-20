# WellTegra ML API

**Cloud-Native API for Physics-Informed Industrial ML**

A Google Cloud Platform service that provides predictive analytics for oil & gas well intervention operations. Built with BigQuery, Cloud Functions, and Vertex AI to predict toolstring failure probability and optimize operational planning.

## 🎯 Purpose

This API demonstrates:
- **Industrial IoT Integration** - Real-time data from operational archives
- **Physics-Informed ML** - Models that understand mechanical physics, not just patterns
- **Cloud-Native Architecture** - Scalable, serverless GCP services
- **Domain Expertise** - 30+ years of offshore well engineering translated into code

## 🏗️ Architecture

```
┌─────────────────┐
│  Frontend       │
│  (welltegra.net)│
└────────┬────────┘
         │ HTTPS
         ▼
┌─────────────────┐
│  Cloud Function │  ← You are here
│  (Flask API)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  BigQuery       │  ← Historical toolstring data
│  (Analytics)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Vertex AI      │  ← ML predictions (future)
│  (ML Models)    │
└─────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Google Cloud Project with billing enabled
- BigQuery dataset with historical data (see setup below)
- `gcloud` CLI installed and authenticated

### Local Development

```bash
# Clone repository
git clone https://github.com/kenmck3772/welltegra-ml-api.git
cd welltegra-ml-api

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GCP_PROJECT_ID=portfolio-project-481815
export BIGQUERY_DATASET=welltegra_historical

# Run locally
python main.py

# Test endpoint
curl http://localhost:8080/api/v1/runs
```

### Deploy to Cloud Functions

```bash
# Deploy to GCP
gcloud functions deploy welltegra-api \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point api \
  --set-env-vars GCP_PROJECT_ID=portfolio-project-481815,BIGQUERY_DATASET=welltegra_historical

# Get function URL
gcloud functions describe welltegra-api --format='value(httpsTrigger.url)'
```

## 📡 API Endpoints

### GET `/api/v1/runs`
Get all historical toolstring runs

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "data": [
    {
      "run_id": "byford-r16",
      "run_name": "Byford R16",
      "well_name": "Anonymized",
      "tool_count": 8,
      "total_length": 61.1,
      "max_od": 4.75
    }
  ]
}
```

### GET `/api/v1/runs/{run_id}`
Get detailed information about a specific run

**Response:**
```json
{
  "status": "success",
  "data": {
    "run_id": "byford-r16",
    "run_name": "Byford R16",
    "tools": [
      {
        "position": 1,
        "tool_name": "Landing Sub",
        "od": 3.5,
        "length": 1.2,
        "category": "drillstring"
      }
    ],
    "stats": {
      "tool_count": 8,
      "total_length": 61.1,
      "max_od": 4.75
    }
  }
}
```

### GET `/api/v1/tools`
Get tool usage statistics

**Query Parameters:**
- `category` - Filter by tool category (fishing, completion, drillstring)
- `limit` - Limit results (default: 50)

**Response:**
```json
{
  "status": "success",
  "count": 18,
  "data": [
    {
      "tool_name": "Fishing Jars",
      "usage_count": 2,
      "avg_od": 3.25,
      "avg_length": 7.9,
      "category": "fishing"
    }
  ]
}
```

### POST `/api/v1/predict` (Coming Soon)
Predict stuck-in-hole probability for a toolstring configuration

**Request:**
```json
{
  "tools": [
    {"name": "Packer", "od": 7.0, "length": 4.2},
    {"name": "Seal Assembly", "od": 5.5, "length": 2.0}
  ],
  "well_conditions": {
    "max_deviation": 35.0,
    "depth": 3500
  }
}
```

**Response:**
```json
{
  "status": "success",
  "prediction": {
    "stuck_probability": 0.23,
    "risk_level": "medium",
    "recommendations": [
      "Consider jarring capability at deviation >30°",
      "Add accelerator above packer for improved pull force"
    ]
  }
}
```

## 🗄️ BigQuery Setup

This API requires historical toolstring data in BigQuery:

### 1. Upload Data

```bash
# From welltegra.network repository
cd ../welltegra.network
python3 scripts/upload-to-bigquery.py
```

### 2. Verify Tables

Tables required:
- `welltegra_historical.toolstring_runs`
- `welltegra_historical.toolstring_tools`

### 3. Test Query

```sql
SELECT
  run_name,
  tool_count,
  total_length
FROM `portfolio-project-481815.welltegra_historical.toolstring_runs`
```

## 🧪 Testing

```bash
# Run unit tests
pytest tests/

# Run with coverage
pytest --cov=api tests/

# Test specific endpoint
pytest tests/test_api.py::test_get_runs
```

## 📊 Monitoring & Logging

**Cloud Functions Logs:**
```bash
gcloud functions logs read welltegra-api --limit 50
```

**BigQuery Usage:**
```sql
SELECT
  query,
  total_bytes_processed,
  total_slot_ms
FROM `region-us`.INFORMATION_SCHEMA.JOBS_BY_PROJECT
WHERE creation_time > TIMESTAMP_SUB(CURRENT_TIMESTAMP(), INTERVAL 1 DAY)
ORDER BY creation_time DESC
LIMIT 10
```

## 💰 Cost Optimization

- **Cloud Functions**: 2M free invocations/month
- **BigQuery**: 1 TB free queries/month, 10 GB free storage
- **Estimated monthly cost**: $0-5 (within free tier for portfolio use)

## 🔐 Security

- **API Authentication**: Cloud Functions IAM (production requires API keys)
- **BigQuery**: Service account with read-only access
- **CORS**: Configured for welltegra.network domain
- **Rate Limiting**: Cloud Armor (optional, for production)

## 🚧 Roadmap

- [x] Basic API with BigQuery integration
- [x] Historical runs and tools endpoints
- [ ] Vertex AI integration for predictions
- [ ] Caching layer (Cloud Memorystore)
- [ ] Realtime updates (Cloud Pub/Sub)
- [ ] GraphQL endpoint
- [ ] Looker Studio dashboard
- [ ] WebSocket for live monitoring

## 🏆 Key Differentiators

**Why this matters for Google interviews:**

1. **Cloud-Native Architecture** - Serverless, scalable, production-ready
2. **Domain Expertise Integration** - Not generic CRUD, physics-informed
3. **Real Data Pipeline** - Actual operational data, not synthetic
4. **ML-Ready Foundation** - Schema designed for Vertex AI training
5. **Cost-Optimized** - Runs entirely in free tier

## 📚 Technologies

- **Runtime**: Python 3.11
- **Framework**: Flask (Cloud Functions)
- **Database**: Google BigQuery
- **ML**: Vertex AI (planned)
- **Deployment**: Cloud Functions / Cloud Run
- **Monitoring**: Cloud Logging, Cloud Monitoring
- **Testing**: pytest, coverage

## 🤝 Contributing

This is a portfolio project demonstrating GCP expertise for career development.

## 📄 License

MIT License - Educational/Portfolio purposes

## 👤 Author

**Ken McKenzie**
- 30+ years offshore well engineering experience
- Transitioning to Cloud ML Engineering
- LinkedIn: [Your LinkedIn]
- Portfolio: https://welltegra.network

---

**Status**: 🟢 Active Development
**Deployment**: Cloud Functions (US-Central1)
**Last Updated**: December 2025
