# Personalization and State Management

## Overview
Make the family assistant more personalized by tracking children's information dynamically and maintaining recommendation history.

## Progress Summary
- ✅ **Task #1: Dynamic Children Age Calculation** - COMPLETED (2025-12-21)
- ⏳ **Task #2: Children Interests Data Store** - Not Started
- ⏳ **Task #3: Recommendation History Database** - Not Started

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
**Status:** Not Started  
**Priority:** Medium  
**Dependencies:** Task #1

**Current State:**
- No tracking of individual children's interests
- AI makes generic recommendations

**Implementation Approach:**

**Option A: Simple Config File (Quick Start)**
```python
# family_config.py
CHILDREN = [
    {
        "name": "Child1",
        "birthdate": "2019-XX-XX",
        "interests": ["dinosaurs", "science", "outdoor play", "animals"]
    },
    {
        "name": "Child2", 
        "birthdate": "2019-XX-XX",
        "interests": ["art", "crafts", "reading", "dancing"]
    },
    {
        "name": "Child3",
        "birthdate": "2022-XX-XX", 
        "interests": ["playgrounds", "animals", "music", "water play"]
    }
]
```

**Option B: Firestore Storage (Future-Proof)**
```
Collection: children
  Document: child_1
    - name: string
    - birthdate: timestamp
    - interests: array
    - favorite_places: array
    - last_updated: timestamp
```

**Integration with AI:**
1. Create helper function to format interests for system prompt:
   ```python
   def get_children_info_for_prompt():
       info = []
       for child in CHILDREN:
           ages = calculate_age(child['birthdate'])
           interests = ", ".join(child['interests'])
           info.append(f"Child (age {age}): interests include {interests}")
       return "; ".join(info)
   ```

2. Update system prompt to include personalized interests

**Benefits:**
- More targeted recommendations
- Can evolve as children grow
- Helps avoid suggesting age-inappropriate activities

---

### 3. Recommendation History Database
**Status:** Not Started  
**Priority:** Medium  
**Files:** New `database.py`, modify `family_manager.py`

**Purpose:**
Prevent recommending the same venues/events repeatedly by tracking what's been suggested.

**Database Schema (Firestore):**
```
Collection: recommendations
  Document: {date}_{recommendation_id}
    - date: timestamp
    - venues: array[string]
    - events: array[string]
    - weather_conditions: string
    - selected_activities: array[object]
      - venue: string
      - event: string
      - reason: string
```

**Implementation:**
1. After generating recommendations, save to Firestore
2. Before generating new recommendations, query recent history (last 30 days)
3. Pass recent venues to system prompt: "Recently visited: X, Y, Z. Suggest different places."

**Benefits:**
- Avoid repetitive suggestions
- Track what works well
- Historical data for future improvements

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

## Next Steps
1. Start with simple config file approach (Task #1 & #2 Option A)
2. Test with dynamic ages in recommendations
3. Plan Firestore migration for Task #3
4. Implement recommendation tracking
