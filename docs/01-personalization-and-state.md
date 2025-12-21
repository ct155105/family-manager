# Personalization and State Management

## Overview
Make the family assistant more personalized by tracking children's information dynamically and maintaining recommendation history.

## Tasks

### 1. Dynamic Children Age Calculation
**Status:** Not Started  
**Priority:** High  
**Files to Modify:** `family_manager.py`

**Current State:**
- Ages are hardcoded as "3, 5, and 7" in system prompt
- Daughter is actually 6, not 5

**Implementation:**
1. Create a `family_config.py` or JSON config file to store:
   ```python
   CHILDREN = [
       {"name": "Child1", "birthdate": "2019-XX-XX"},
       {"name": "Child2", "birthdate": "2019-XX-XX"},
       {"name": "Child3", "birthdate": "2022-XX-XX"}
   ]
   ```
2. Create utility function to calculate current ages:
   ```python
   from datetime import datetime
   
   def get_children_ages():
       today = datetime.now()
       ages = []
       for child in CHILDREN:
           birth = datetime.strptime(child['birthdate'], '%Y-%m-%d')
           age = (today - birth).days // 365
           ages.append(age)
       return ages
   ```
3. Update system prompt in `family_manager.py` to use dynamic ages:
   ```python
   ages = get_children_ages()
   age_string = ", ".join(str(age) for age in ages)
   SYSTEM_PROMPT = f"The family has 3 children, ages {age_string}..."
   ```

**Benefits:**
- Always accurate ages
- Single source of truth for family data
- Easy to maintain as children grow

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
