# Firestore Setup Guide

## Overview
This guide walks through setting up Google Cloud Firestore for the family-manager recommendation history feature.

## 🎓 Teaching: Authentication Patterns for Agents

When building agents that use cloud services, you have several authentication options:

```
┌────────────────────────────────────────────────────┐
│ Pattern              │ Use Case                    │
├────────────────────────────────────────────────────┤
│ Application Default  │ Local Development (we use)  │
│ Credentials (ADC)    │ - Uses your Google account  │
│                      │ - No file management        │
│                      │ - Auto-rotating tokens      │
├────────────────────────────────────────────────────┤
│ Service Account      │ Production / CI/CD          │
│ (JSON key file)      │ - Server-side agents        │
│                      │ - GitHub Actions secrets    │
│                      │ - Automated workflows       │
├────────────────────────────────────────────────────┤
│ Workload Identity    │ Cloud-native (best)         │
│                      │ - Cloud Run, GKE            │
│                      │ - No files or keys needed   │
└────────────────────────────────────────────────────┘
```

**Why ADC for local development?**
- ✅ No JSON files to manage or accidentally commit
- ✅ Uses your existing Google account
- ✅ Automatic token refresh (no expiration issues)
- ✅ Same code works in production (SDK auto-detects environment)

---

## Step-by-Step Setup

### 1. Create/Select GCP Project

**Option A: Use existing Firebase/GCP project**
- Note your project ID (e.g., `ct-dev-playground`)

**Option B: Create new Firebase project**
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Name it: `family-manager` (or your preferred name)
4. Disable Google Analytics (not needed for this use case)
5. Click "Create project"

### 2. Enable Firestore Database

1. In Firebase Console, click "Firestore Database" in left sidebar
2. Click "Create database"
3. **Security rules:** Start in **test mode** (we'll secure it later)
4. **Location:** Choose `us-central1` (or nearest to you)
5. Click "Enable"

**Teaching Note: Security Rules**
```javascript
// Test mode (TEMPORARY - for development)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /{document=**} {
      allow read, write: if true;  // ⚠️ INSECURE - anyone can access
    }
  }
}

// Production mode (switch to this after testing)
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /recommendations/{docId} {
      // Only authenticated service accounts can read/write
      allow read, write: if request.auth != null;
    }
  }
}
```

### 3. Install gcloud CLI

```bash
# macOS with Homebrew
brew install google-cloud-sdk

# Restart terminal or source your shell config
source ~/.zshrc  # or ~/.bashrc
```

### 4. Authenticate with ADC

```bash
# This opens a browser for Google OAuth
gcloud auth application-default login

# Set your default project
gcloud config set project YOUR_PROJECT_ID
```

**What happens:**
1. Browser opens → Google login page
2. You authorize "Google Auth Library"
3. Token saved to `~/.config/gcloud/application_default_credentials.json`
4. Any app using ADC can now authenticate as you

### 5. Update .env File

Add to your `.env` file:

```bash
# Firestore Configuration (using Application Default Credentials)
# Auth: Run `gcloud auth application-default login` to authenticate
FIRESTORE_PROJECT_ID=your-project-id

# Optional: Override collection for testing
# FIRESTORE_COLLECTION=recommendations_test
```

### 6. Install Required Dependencies

```bash
pip install google-cloud-firestore python-dotenv
```

Add to `requirements.txt`:
```
google-cloud-firestore>=2.14.0
python-dotenv
```

### 7. Verify Setup

Run the test script:
```bash
python tests/test_firestore_connection.py
```

Expected output:
```
🚀 Firestore Setup Verification
📁 Using collection: recommendations_test (isolated from production)
✅ Successfully connected to Firestore!
📍 Project: your-project-id
📁 Collection: recommendations_test
✅ Using test collection (production data protected)
🎉 All tests passed!
```

---

## 🎓 Teaching: Credential Management Patterns

### Local Development (ADC)
```
Your Machine
├── ~/.config/gcloud/
│   └── application_default_credentials.json  # Created by gcloud auth
├── family-manager/
│   ├── .env                          # Contains FIRESTORE_PROJECT_ID
│   ├── recommendation_db.py          # Uses ADC automatically
│   └── family_manager.py
```

### Production Deployment

**Pattern 1: Cloud Run / GKE (Recommended)**
```yaml
# Use Workload Identity (no JSON files!)
# GCP automatically provides credentials to your service
- Your agent runs on Cloud Run
- Assign service account to Cloud Run service
- No credentials file needed
- Set FIRESTORE_PROJECT_ID as env var
```

**Pattern 2: GitHub Actions (CI/CD)**
```yaml
# Store credentials as GitHub Secret
- name: Authenticate to GCP
  uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_CREDENTIALS }}

- name: Run agent
  env:
    FIRESTORE_PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
```

**Pattern 3: Local Server / Cron Job**
```bash
# Option A: Use ADC (if you've run gcloud auth)
export FIRESTORE_PROJECT_ID=your-project-id

# Option B: Use service account JSON
export GOOGLE_APPLICATION_CREDENTIALS=/secure/path/creds.json
export FIRESTORE_PROJECT_ID=your-project-id
```

---

## Troubleshooting

### Error: "FIRESTORE_PROJECT_ID not set"

**Solution:**
```bash
# Add to .env file
echo "FIRESTORE_PROJECT_ID=your-project-id" >> .env

# Or set environment variable
export FIRESTORE_PROJECT_ID=your-project-id
```

### Error: "Could not automatically determine credentials"

**Solution:**
```bash
# Re-authenticate with gcloud
gcloud auth application-default login

# Verify credentials exist
ls ~/.config/gcloud/application_default_credentials.json
```

### Error: "Permission denied" or "403 Forbidden"

**Solution:**
1. Verify your Google account has access to the project
2. Go to IAM & Admin in GCP Console
3. Check that your email has `Cloud Datastore User` or `Firebase Admin` role
4. If using service account, verify its roles

### Error: "Could not find credentials"

**Solution:**
```bash
# Check if ADC credentials exist
cat ~/.config/gcloud/application_default_credentials.json

# If not, re-authenticate
gcloud auth application-default login
```

---

## Testing Best Practices

### Collection Separation Pattern

Tests use a separate collection to avoid polluting production data:

```python
# In test files, set before importing
import os
os.environ['FIRESTORE_COLLECTION'] = 'recommendations_test'

# Then import - singleton uses test collection
from recommendation_db import get_db
```

### Clean Up Test Data

The test script automatically cleans up after itself. For manual cleanup:

```bash
python cleanup_test_data.py
```

---

## Security Checklist

Before going to production:

- [ ] Firestore security rules configured (not test mode)
- [ ] Using service account (not personal ADC) in production
- [ ] Service account has minimal permissions (least privilege)
- [ ] FIRESTORE_PROJECT_ID set via secure secret management
- [ ] Audit logs enabled in GCP
- [ ] Test collection separated from production

---

## Completed!

Once Firestore is set up:
1. ✅ Test the connection: `python tests/test_firestore_connection.py`
2. ✅ Run the agent: `python family_manager.py`
3. ✅ Verify history is saved and loaded

See [01-personalization-and-state.md](01-personalization-and-state.md) for implementation details.

