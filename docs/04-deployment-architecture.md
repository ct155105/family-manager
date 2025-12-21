# GCP Deployment Architecture

## Overview
Deploy the Family Manager assistant to Google Cloud Platform for automated daily execution and production-ready operation.

## Current State
- **Environment:** Local development only
- **Execution:** Manual (`python family_manager.py`)
- **State:** No persistence (except Gmail drafts)
- **Scheduling:** None

## Target State
- **Environment:** Google Cloud Platform
- **Execution:** Automated daily via Cloud Scheduler
- **State:** Firestore database
- **Monitoring:** Cloud Logging & Error Reporting
- **Secrets:** Secret Manager

---

## Architecture Design

### Component Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Cloud Scheduler                             │
│              (Daily trigger at 7:00 AM EST)                     │
└────────────────────────┬────────────────────────────────────────┘
                         │ HTTP POST
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Cloud Run Service                            │
│                  (family-manager-service)                        │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Container: family-manager:latest                         │  │
│  │  - Python 3.12                                            │  │
│  │  - LangChain + LangGraph                                  │  │
│  │  - BeautifulSoup (scrapers)                               │  │
│  │  - Google Cloud libraries                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  Environment Variables from Secret Manager                       │
└────────┬────────────┬────────────────┬────────────────┬─────────┘
         │            │                │                │
         ▼            ▼                ▼                ▼
   ┌─────────┐  ┌─────────┐    ┌──────────┐    ┌──────────┐
   │ Secret  │  │Firestore│    │  Gmail   │    │ OpenAI   │
   │ Manager │  │   DB    │    │   API    │    │   API    │
   └─────────┘  └─────────┘    └──────────┘    └──────────┘
```

---

## Task 16: Design GCP Architecture

**Status:** Not Started  
**Priority:** High

### Service Selection

#### Cloud Run (Recommended)
**Why:**
- Serverless (pay per use)
- Auto-scaling (scales to zero when not running)
- Easy deployments
- HTTP endpoint for Cloud Scheduler
- Suitable for scheduled jobs

**Configuration:**
```yaml
Service: family-manager-service
Memory: 1 GB
CPU: 1
Timeout: 900s (15 minutes)
Concurrency: 1 (only one instance needed)
Min instances: 0 (scale to zero)
Max instances: 1 (prevent parallel runs)
```

#### Alternative: Cloud Functions
- Simpler but more limited (timeout, dependencies)
- Good if keeping deployment minimal
- May struggle with heavy dependencies

#### Not Recommended: Compute Engine
- Overkill for scheduled task
- Always-on = higher cost
- More management overhead

---

### Data Architecture

#### Firestore Database

**Database:** Firestore Native Mode  
**Location:** us-central1 (or closest to you)

**Collections Structure:**
```
family-manager-prod/
├── children/
│   ├── child_1
│   │   ├── name: string
│   │   ├── birthdate: timestamp
│   │   ├── interests: array<string>
│   │   └── updated_at: timestamp
│   ├── child_2
│   └── child_3
│
├── recommendations/
│   ├── 2025-12-21_abc123
│   │   ├── date: timestamp
│   │   ├── weather_summary: string
│   │   ├── weather_temp_high: number
│   │   ├── weather_temp_low: number
│   │   ├── recommendations: array<object>
│   │   │   ├── rank: number
│   │   │   ├── venue: string
│   │   │   ├── activity: string
│   │   │   ├── reasoning: string
│   │   │   └── details: object
│   │   ├── email_sent: boolean
│   │   ├── draft_id: string
│   │   └── created_at: timestamp
│   └── ...
│
├── venues/
│   ├── columbus_zoo
│   │   ├── name: string
│   │   ├── address: string
│   │   ├── url: string
│   │   ├── indoor_outdoor: string
│   │   ├── typical_duration_hours: number
│   │   ├── last_visited: timestamp
│   │   └── visit_count: number
│   └── ...
│
└── config/
    └── settings
        ├── email_recipients: array<string>
        ├── max_recommendations: number
        ├── lookback_days: number
        └── updated_at: timestamp
```

**Indexes:**
- `recommendations` collection: Index on `date` (descending)
- `venues` collection: Index on `last_visited` (descending)

---

### Secrets Management

#### Secret Manager Secrets

```
projects/YOUR_PROJECT/secrets/
├── openai-api-key
│   └── latest: "sk-..."
├── openweathermap-api-key
│   └── latest: "..."
├── gmail-credentials
│   └── latest: {"installed": {...}}
└── gmail-token
    └── latest: {"token": "...", "refresh_token": "..."}
```

**Access Pattern:**
```python
from google.cloud import secretmanager

def get_secret(secret_id):
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Usage
OPENAI_API_KEY = get_secret("openai-api-key")
```

---

### IAM & Permissions

#### Service Account
**Name:** `family-manager-sa@PROJECT_ID.iam.gserviceaccount.com`

**Roles:**
- `roles/datastore.user` - Read/write Firestore
- `roles/secretmanager.secretAccessor` - Read secrets
- `roles/logging.logWriter` - Write logs
- `roles/cloudtrace.agent` - Trace requests

**Gmail API:**
- Handled via OAuth token stored in Secret Manager
- No additional IAM needed

---

### Networking

**VPC:** Default VPC (sufficient for this use case)  
**Egress:** 
- Allow all (needed for external APIs: OpenAI, Weather, web scraping)
- Future: VPC Service Controls for production hardening

**Ingress:**
- Cloud Run service: Allow Cloud Scheduler only
- Use Cloud Run's built-in authentication

---

## Task 17: Create Deployment Configuration

**Status:** Not Started  
**Priority:** High  
**Dependencies:** Task 16

### Files to Create

#### 1. Dockerfile
```dockerfile
# /Dockerfile
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run the application
CMD ["python", "family_manager.py"]
```

#### 2. Cloud Build Configuration
```yaml
# cloudbuild.yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'build'
      - '-t'
      - 'gcr.io/$PROJECT_ID/family-manager:$COMMIT_SHA'
      - '-t'
      - 'gcr.io/$PROJECT_ID/family-manager:latest'
      - '.'
  
  # Push to Container Registry
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/family-manager:$COMMIT_SHA'
  
  - name: 'gcr.io/cloud-builders/docker'
    args:
      - 'push'
      - 'gcr.io/$PROJECT_ID/family-manager:latest'
  
  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    entrypoint: gcloud
    args:
      - 'run'
      - 'deploy'
      - 'family-manager-service'
      - '--image=gcr.io/$PROJECT_ID/family-manager:$COMMIT_SHA'
      - '--region=us-central1'
      - '--platform=managed'
      - '--service-account=family-manager-sa@$PROJECT_ID.iam.gserviceaccount.com'
      - '--memory=1Gi'
      - '--timeout=900s'
      - '--max-instances=1'
      - '--min-instances=0'
      - '--no-allow-unauthenticated'

images:
  - 'gcr.io/$PROJECT_ID/family-manager:$COMMIT_SHA'
  - 'gcr.io/$PROJECT_ID/family-manager:latest'

options:
  logging: CLOUD_LOGGING_ONLY
```

#### 3. Terraform (Infrastructure as Code)
```hcl
# terraform/main.tf
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Service Account
resource "google_service_account" "family_manager" {
  account_id   = "family-manager-sa"
  display_name = "Family Manager Service Account"
}

# IAM Roles
resource "google_project_iam_member" "firestore_user" {
  project = var.project_id
  role    = "roles/datastore.user"
  member  = "serviceAccount:${google_service_account.family_manager.email}"
}

resource "google_project_iam_member" "secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.family_manager.email}"
}

# Firestore Database
resource "google_firestore_database" "database" {
  name        = "(default)"
  location_id = var.region
  type        = "FIRESTORE_NATIVE"
}

# Cloud Scheduler Job
resource "google_cloud_scheduler_job" "daily_recommendations" {
  name             = "daily-family-recommendations"
  description      = "Trigger family recommendations at 7 AM daily"
  schedule         = "0 7 * * *"
  time_zone        = "America/New_York"
  attempt_deadline = "900s"

  http_target {
    http_method = "POST"
    uri         = google_cloud_run_service.family_manager.status[0].url
    
    oidc_token {
      service_account_email = google_service_account.family_manager.email
    }
  }
}

# Cloud Run Service (managed externally via Cloud Build)
data "google_cloud_run_service" "family_manager" {
  name     = "family-manager-service"
  location = var.region
}
```

#### 4. Environment Configuration
```python
# config/gcp_config.py
import os
from google.cloud import secretmanager
from google.cloud import firestore

# Determine environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# GCP Project
PROJECT_ID = os.getenv("GCP_PROJECT_ID", "your-project-id")

# Secret Manager
def get_secret(secret_id: str) -> str:
    """Retrieve secret from Secret Manager or environment variable."""
    # In local dev, use .env file
    if not IS_PRODUCTION:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(secret_id.upper().replace("-", "_"))
    
    # In production, use Secret Manager
    client = secretmanager.SecretManagerServiceClient()
    name = f"projects/{PROJECT_ID}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

# Firestore Client
def get_firestore_client():
    """Get Firestore client."""
    return firestore.Client(project=PROJECT_ID)

# API Keys
OPENAI_API_KEY = get_secret("openai-api-key")
WEATHER_API_KEY = get_secret("openweathermap-api-key")
```

---

### Deployment Scripts

#### Setup Script
```bash
#!/bin/bash
# scripts/setup_gcp.sh

set -e

PROJECT_ID="your-project-id"
REGION="us-central1"

echo "Setting up GCP project: $PROJECT_ID"

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  cloudscheduler.googleapis.com \
  --project=$PROJECT_ID

# Create service account
gcloud iam service-accounts create family-manager-sa \
  --display-name="Family Manager Service Account" \
  --project=$PROJECT_ID

# Grant IAM roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:family-manager-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/datastore.user"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:family-manager-sa@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Create secrets
echo "Creating secrets..."
echo -n "YOUR_OPENAI_KEY" | gcloud secrets create openai-api-key \
  --data-file=- \
  --project=$PROJECT_ID

echo -n "YOUR_WEATHER_KEY" | gcloud secrets create openweathermap-api-key \
  --data-file=- \
  --project=$PROJECT_ID

# Initialize Firestore
gcloud firestore databases create --region=$REGION --project=$PROJECT_ID

echo "GCP setup complete!"
```

#### Deploy Script
```bash
#!/bin/bash
# scripts/deploy.sh

set -e

PROJECT_ID="your-project-id"
REGION="us-central1"

echo "Deploying Family Manager to Cloud Run..."

gcloud builds submit \
  --config=cloudbuild.yaml \
  --project=$PROJECT_ID

echo "Deployment complete!"
```

---

## Task 18: Implement Deployment

**Status:** Not Started  
**Dependencies:** Tasks 16, 17  
**Priority:** High

### Deployment Steps

1. **Initial Setup:**
   ```bash
   ./scripts/setup_gcp.sh
   ```

2. **Configure Secrets:**
   - Upload API keys to Secret Manager
   - Upload Gmail OAuth credentials/token

3. **Deploy Application:**
   ```bash
   ./scripts/deploy.sh
   ```

4. **Verify Deployment:**
   ```bash
   gcloud run services describe family-manager-service \
     --region=us-central1 \
     --project=your-project-id
   ```

5. **Test Manually:**
   ```bash
   gcloud run services proxy family-manager-service \
     --region=us-central1
   ```

6. **Setup Scheduler:**
   ```bash
   terraform apply
   ```

7. **Monitor First Scheduled Run:**
   - Check Cloud Logging
   - Verify email sent
   - Check Firestore data

---

## Monitoring & Observability

### Cloud Logging
- All print statements go to Cloud Logging
- Filter: `resource.type="cloud_run_revision"`

### Error Reporting
- Automatically captures Python exceptions
- Email alerts on errors

### Alerting Policies
1. **Failed Executions:** Alert if job fails 2 days in a row
2. **High Costs:** Alert if daily cost exceeds threshold
3. **No Emails Sent:** Alert if no draft created in 7 days

---

## Cost Estimation

### Monthly Costs (Estimated)

| Service | Usage | Cost |
|---------|-------|------|
| Cloud Run | 1 run/day, ~2 min | ~$0.50 |
| Firestore | Read/writes, storage | ~$1.00 |
| Secret Manager | 6 secrets, 30 accesses/day | ~$0.20 |
| Cloud Scheduler | 1 job | $0.10 |
| Cloud Build | ~5 builds/month | ~$0.50 |
| Networking | Minimal egress | ~$0.50 |
| **Total** | | **~$2.80/month** |

**Note:** Actual costs may vary. OpenAI API costs are separate.

---

## Security Best Practices

1. **Least Privilege:** Service account has only required permissions
2. **Secret Rotation:** Rotate API keys periodically
3. **No Public Access:** Cloud Run service not publicly accessible
4. **Audit Logs:** Enable for sensitive operations
5. **VPC:** Consider VPC for enhanced security
6. **Container Scanning:** Enable vulnerability scanning

---

## Future Enhancements

1. **CI/CD Pipeline:** GitHub Actions → Cloud Build → Cloud Run
2. **Blue/Green Deployments:** Test new versions safely
3. **Multi-Region:** Disaster recovery
4. **Backup Strategy:** Firestore exports to Cloud Storage
5. **Cost Optimization:** Analyze and optimize API calls
