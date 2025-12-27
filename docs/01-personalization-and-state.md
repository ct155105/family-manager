# Personalization and State Management

## Overview
Make the family assistant more personalized by tracking children's information dynamically and maintaining recommendation history.

## Progress Summary
- ✅ **Task #1: Dynamic Children Age Calculation** - COMPLETED (2025-12-21)
- ✅ **Task #2: Children Interests Data Store** - COMPLETED (2025-12-21)
- ✅ **Task #3: Recommendation History Database** - COMPLETED (2025-12-26)

---

## Tasks

### 1. Dynamic Children Age Calculation
**Status:** ✅ COMPLETED (2025-12-21)
**Priority:** High
**Files Modified:** `family_manager.py`, `family_config.py` (new), `tests/test_family_config.py` (new)

**What Was Implemented:**
1. ✅ Created `family_config.py` with children's birthdates:
   ```python
   CHILDREN = [
       {"name": "Grayson", "birthdate": "2018-04-27"},  # Age 7
       {"name": "Child2", "birthdate": "2019-12-03"},   # Age 6
       {"name": "Child3", "birthdate": "2022-02-22"}    # Age 3
   ]
   ```

2. ✅ Implemented utility functions:
   - `get_children_ages()` - Calculates current ages dynamically, properly handling birthdays
   - `get_children_age_string()` - Formats ages as "7, 6, and 3" for system prompts

3. ✅ Updated `family_manager.py` to use dynamic ages:
   ```python
   age_string = get_children_age_string()
   SYSTEM_PROMPT = f"The family has 3 children, ages {age_string}..."
   ```

4. ✅ Created comprehensive test suite (14 tests) following TDD:
   - Data structure validation
   - Age calculation accuracy (including edge cases)
   - String formatting
   - All tests passing ✓

**Benefits Delivered:**
- ✅ Always accurate ages (daughter now correctly shown as 6, not 5)
- ✅ Single source of truth for family data
- ✅ Easy to maintain as children grow
- ✅ Well-tested with TDD methodology
- ✅ Proper handling of birthdays throughout the year

---

### 2. Children Interests Data Store
**Status:** ✅ COMPLETED (2025-12-21)
**Priority:** Medium
**Dependencies:** Task #1
**Files Modified:** `family_config.py`, `family_manager.py`

**What Was Implemented:**
1. ✅ Added interests array to each child in `CHILDREN` config:
   - Grayson: art, drawing, animals, reptiles, nature, snakes, science, LEGO, swimming, performing arts
   - Madeline: art, dancing, animals
   - Chase: trucks, trains, animals, playgrounds, music

2. ✅ Created `get_children_interests_string()` function to format interests for prompts

3. ✅ Updated system prompt in `family_manager.py` to include personalized interests

**Benefits Delivered:**
- ✅ AI makes personalized recommendations based on each child's specific interests
- ✅ Age-appropriate activity suggestions aligned with preferences
- ✅ Easy to update as children's interests evolve

---

### 3. Recommendation History Database
**Status:** ✅ COMPLETED (2025-12-26)
**Priority:** Medium
**Files:** New `recommendation_db.py`, modified `family_manager.py`, new `test_firestore_connection.py`

**What Was Implemented:**

1. ✅ **Created `recommendation_db.py` with State Abstraction Layer:**
   - `RecommendationDatabase` class (Repository Pattern)
   - `save_recommendation()` - Persists recommendations to Firestore
   - `get_recent_recommendations()` - Time-windowed queries (last N days)
   - `get_recently_visited_venues()` - Materialized view pattern
   - Singleton pattern for database instance
   - Graceful error handling (degradation if DB unavailable)

2. ✅ **Firestore Schema Design:**
   ```python
   Collection: recommendations
     Document: {auto_id}
       - timestamp: datetime       # Indexed for time-range queries
       - date: string             # Human-readable (YYYY-MM-DD)
       - venues_mentioned: [str]  # Extracted venue names
       - events_mentioned: [str]  # Specific events (optional)
       - weather_conditions: str  # Context for analysis
       - raw_suggestions: str     # Full recommendation text
       - created_by: str          # "family_manager_v1"
       - created_at: timestamp    # Server timestamp
   ```

3. ✅ **Integrated with Agent Pipeline (State Hydration Pattern):**
   - **Pre-fetch:** Load recent venues in `create_messages()` before agent runs
   - **System Prompt:** Add "RECENT ACTIVITY HISTORY" section to avoid repetition
   - **Post-process:** Extract venues with LLM after agent generates recommendations
   - **Persist:** Save to Firestore via new `save_recommendation_to_history` node

4. ✅ **LangGraph Pipeline Updated:**
   ```
   START
     → create_messages (load history, build prompt)
     → get_ideas_for_today (agent generates recommendations)
     → save_recommendation_to_history (extract & persist)
     → generate_newsletter_html (format)
     → create_gmail_draft_from_html (email)
   ```

5. ✅ **Created Setup Documentation:**
   - `docs/FIRESTORE_SETUP.md` - Complete setup guide
   - Authentication patterns explained
   - Security best practices
   - Troubleshooting guide

6. ✅ **Test Infrastructure:**
   - `test_firestore_connection.py` - Verify Firestore setup
   - Tests connection, read, and write operations

**Key Patterns Demonstrated:**
- 🏛️ **Repository Pattern:** Database logic separated from agent logic
- 🚰 **State Hydration:** Load state before agent runs (not via tool)
- 🔄 **Graceful Degradation:** Agent continues if database unavailable
- 📦 **Singleton Pattern:** One database connection per lifecycle
- 🎯 **Materialized View:** Return only needed data (venue names, not full docs)
- 🧩 **Side-Effect Node:** LangGraph node that persists without modifying state
- 🤖 **LLM Post-Processing:** Extract structured data from free-form text

**Benefits Delivered:**
- ✅ Prevents repetitive venue suggestions
- ✅ Tracks recommendation history for future analysis
- ✅ Cloud-based state (accessible across devices)
- ✅ Agent remains stateless (state externalized to Firestore)
- ✅ Can swap storage backend without changing agent code

**Setup Required:**
1. Create Firebase project (or use existing GCP project)
2. Enable Firestore database
3. Install gcloud CLI: `brew install google-cloud-sdk`
4. Authenticate: `gcloud auth application-default login`
5. Set `FIRESTORE_PROJECT_ID` in `.env`
6. Run `pip install google-cloud-firestore>=2.14.0`
7. Test with `python test_firestore_connection.py`

**Authentication:** Uses Application Default Credentials (ADC) - no JSON key files needed for local development.

---

## Configuration Management

### Recommended Structure
```
family-manager/
  config/
    family_config.py          # Children info, interests
    venues_config.py          # Venue metadata (addresses, URLs)
  database/
    firestore_client.py       # Firestore connection & queries
    models.py                 # Data models
  docs/                       # This documentation
```

### Environment Variables
```bash
# .env
FIRESTORE_PROJECT_ID=your-project-id
FIRESTORE_COLLECTION_PREFIX=prod  # or dev
OPENAI_API_KEY=...
OPENWEATHERMAP_API_KEY=...
```

---

## Completed!

All three tasks in this priority are complete:
- ✅ Task #1: Dynamic age calculation
- ✅ Task #2: Children interests
- ✅ Task #3: Recommendation history with Firestore

**Next Priority:** See [02-event-scrapers.md](02-event-scrapers.md) for Priority 3 tasks (COSI, Cedar Point, etc.)
