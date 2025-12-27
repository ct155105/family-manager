# State Management Patterns in Agentic Systems

## Overview
This document explains the state management patterns used in the family-manager project. These are production-grade patterns you'll encounter when building AI agents at scale.

Written during implementation of Task #3 (Recommendation History Database) - December 26, 2025

---

## 🎓 The Three Types of State

Every agentic system deals with three types of state. Understanding which type you're working with helps you choose the right pattern.

### 1. Conversation State (Ephemeral)
**Lifetime:** Single execution
**Scope:** Current conversation only
**Storage:** In-memory (Python variables, LangGraph State)

**Example in our code:**
```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    input_prompt: str
    html: str
    raw_message: str
```

**When to use:**
- Messages passed between agent nodes
- Intermediate processing results
- Temporary calculations

**Pattern:** Just use LangGraph's `State` TypedDict. No persistence needed.

---

### 2. Application State (Session-persistent)
**Lifetime:** Multiple turns in a conversation
**Scope:** One user session
**Storage:** In-memory with checkpointing, or Redis for distributed systems

**Examples:**
- Shopping cart in an e-commerce agent
- Partially filled forms
- Multi-step workflows ("First tell me your budget, then I'll suggest hotels")

**Pattern:** LangGraph's checkpointing mechanism
```python
from langgraph.checkpoint import MemorySaver

# Enable conversation memory
checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)

# Resume conversation with thread_id
graph.invoke(input, config={"configurable": {"thread_id": "user_123"}})
```

**We don't use this yet** because family-manager runs once and generates recommendations. No multi-turn conversation.

---

### 3. Domain State (Persistent)
**Lifetime:** Forever (or until explicitly deleted)
**Scope:** Across all sessions, all users
**Storage:** Database (SQL, NoSQL, Vector stores)

**Examples in our code:**
- Children's birthdates and interests → `family_config.py` (file-based)
- Recommendation history → Firestore (cloud database)

**Pattern:** External storage with abstraction layer (covered below)

---

## 🏗️ Architecture Pattern: State Abstraction

**Problem:** If your agent code directly calls `firestore.collection('recs').add(...)`, you're locked into Firestore. Testing is hard. Swapping databases requires rewriting agent logic.

**Solution:** Repository Pattern + Facade Pattern

### Our Implementation

```
┌─────────────────────────────────────────────┐
│  Agent Layer (family_manager.py)            │
│  • Knows: "I need recent venues"            │
│  • Doesn't know: Where/how data is stored   │
│                                             │
│  get_recently_visited_venues()              │
└──────────────────┬──────────────────────────┘
                   │ Clean Interface
┌──────────────────▼──────────────────────────┐
│  State Manager (recommendation_db.py)       │
│  • Repository Pattern                       │
│  • Knows: Firestore schema, queries         │
│  • Handles: Auth, retry, errors             │
└──────────────────┬──────────────────────────┘
                   │ Firebase SDK
┌──────────────────▼──────────────────────────┐
│  Database (Firestore)                       │
└─────────────────────────────────────────────┘
```

### Code Example

**❌ BAD - Tight coupling:**
```python
# family_manager.py
from google.cloud import firestore

def create_messages(state):
    db = firestore.Client()
    docs = db.collection('recommendations').where('timestamp', '>=', cutoff).get()
    venues = [v for doc in docs for v in doc.to_dict()['venues']]
    # ... build prompt
```

**✅ GOOD - Abstraction layer:**
```python
# family_manager.py
from recommendation_db import get_recently_visited_venues

def create_messages(state):
    venues = get_recently_visited_venues(days=30)
    # ... build prompt
```

**Benefits:**
- Agent code stays clean and readable
- Easy to test (mock `get_recently_visited_venues()`)
- Can swap Firestore for Postgres without touching agent
- Database logic isolated (easier to optimize queries)

---

## 🚰 Pattern: State Hydration

**Question:** Should state be loaded via an agent tool, or pre-fetched before the agent runs?

### Decision Framework

| Factor | Pre-fetch | Tool |
|--------|-----------|------|
| **Frequency** | Always needed (100% of runs) | Sometimes needed (<50%) |
| **Size** | Small (<10KB) | Large (>100KB) or varies |
| **Latency** | Fast query (<100ms) | Slow query (>1s) |
| **User-driven** | No (agent always needs it) | Yes (depends on user input) |

### Our Choice: Pre-fetch (State Hydration)

```python
def create_messages(state: State) -> list:
    """
    Pre-fetch all context before agent runs.

    Pattern: State Hydration
    - Load state BEFORE agent runs
    - Put in system prompt
    - Agent uses it automatically
    """
    # Pre-fetch (happens before agent sees prompt)
    age_string = get_children_age_string()
    interests_string = get_children_interests_string()
    weather_forecast = get_weekend_forecast.invoke({})
    recently_visited = get_recently_visited_venues(days=30)

    # Inject into system prompt
    SYSTEM_PROMPT = f"""...
    RECENT ACTIVITY HISTORY:
    Recently visited: {', '.join(recently_visited)}
    Please suggest DIFFERENT venues.
    ...
    """
```

**Why this pattern?**
- ✅ We ALWAYS need recent venues (100% of runs)
- ✅ Query is fast (<100ms)
- ✅ Data is small (list of venue names)
- ✅ Agent can't forget to check (reliability)
- ✅ Fewer tool calls = faster, cheaper

### Alternative: Tool Pattern

**When to use tools for state:**
```python
@tool
def search_recommendation_history(venue_name: str, days: int = 30) -> str:
    """
    Search past recommendations for a specific venue.

    Use when:
    - User asks: "Have we been to the zoo recently?"
    - Agent needs to check specific venues (not all)
    - Conditional access based on conversation
    """
    # ... query logic
```

**Use case:** Chatbot where user drives queries: "When did we last go to the zoo?"

---

## 🔄 Pattern: Graceful Degradation

**Principle:** Database failures shouldn't crash your agent.

### Our Implementation

```python
def create_messages(state: State) -> list:
    try:
        recently_visited = get_recently_visited_venues(days=30)
        if recently_visited:
            recent_venues_text = f"Recently visited: {', '.join(recently_visited)}..."
        else:
            recent_venues_text = ""
    except Exception as e:
        # Graceful degradation: Continue without history
        print(f"⚠️  Could not load recommendation history: {e}")
        recent_venues_text = ""

    # Agent still runs, just without history context
    SYSTEM_PROMPT = f"...{recent_venues_text}..."
```

**Benefits:**
- Agent continues working even if Firestore is down
- Better user experience (suggestions still generated)
- Easier to develop (can test without database)

**When to fail hard instead:**
```python
# If data is CRITICAL, fail fast
user_profile = get_user_profile(user_id)  # No try/except
if not user_profile:
    raise ValueError("Cannot generate recommendations without user profile")
```

---

## 🧩 Pattern: Side-Effect Nodes in LangGraph

**Problem:** You want to save data to a database, but don't want to modify the conversation state.

**Solution:** Create a "pass-through" node that performs side effects.

### Our Implementation

```python
def save_recommendation_to_history(state: State) -> dict:
    """
    Pattern: Side-Effect Node
    - Reads from state (raw_message)
    - Saves to external system (Firestore)
    - Returns empty dict (doesn't modify state)
    """
    raw_message = state.get("raw_message", "")

    # Extract venues (side effect: LLM call)
    venues = extract_venues_with_llm(raw_message)

    # Save to database (side effect: Firestore write)
    save_recommendation(raw_message, venues)

    # Return empty dict - state flows through unchanged
    return {}

# In graph
graph_builder.add_edge("get_ideas_for_today", "save_recommendation_to_history")
graph_builder.add_edge("save_recommendation_to_history", "generate_newsletter_html")
```

**Why return `{}`?**
- LangGraph requires all nodes to return a dict
- Empty dict means "no changes to state"
- Next node receives state exactly as previous node left it

**Graph Flow:**
```
get_ideas_for_today
  ↓ state = {messages: [...], raw_message: "Visit the zoo..."}
save_recommendation_to_history
  • Reads: state['raw_message']
  • Side effects: Firestore.save(...)
  • Returns: {}
  ↓ state unchanged = {messages: [...], raw_message: "Visit the zoo..."}
generate_newsletter_html
  • Uses: state['raw_message']
```

---

## 🤖 Pattern: LLM Post-Processing

**Problem:** Your agent outputs free-form text, but you need structured data for your database.

**Solutions:**

### A. Structured Output (Function Calling) - Best for Production
```python
from langchain.output_parsers import PydanticOutputParser
from pydantic import BaseModel

class Recommendation(BaseModel):
    venues: List[str]
    reasoning: str

agent = create_react_agent(
    model="gpt-4",
    tools=tools,
    output_parser=PydanticOutputParser(pydantic_object=Recommendation)
)
```

**Pros:** Reliable, type-safe, no parsing errors
**Cons:** Requires agent changes, more complex

### B. Post-Processing with LLM - What We Used
```python
def save_recommendation_to_history(state: State) -> dict:
    raw_message = state.get("raw_message", "")

    # Use cheap model for extraction
    extractor = init_chat_model(model="gpt-4o-mini", temperature=0)

    extraction_prompt = f"""
    Extract venue names from these recommendations.
    Return ONLY a JSON array: ["Venue 1", "Venue 2"]

    Recommendations: {raw_message}
    """

    response = extractor.invoke([{"role": "user", "content": extraction_prompt}])
    venues = json.loads(response.content)

    save_recommendation(raw_message, venues)
    return {}
```

**Pros:**
- ✅ Quick to implement
- ✅ Flexible (works with any agent output format)
- ✅ Separation of concerns (extraction decoupled from generation)

**Cons:**
- Extra LLM call (cost ~$0.001/extraction with gpt-4o-mini)
- Potential parsing failures (mitigate with error handling)

**Why we chose this:**
- Faster to build (learning project priority)
- Demonstrates "LLMs calling LLMs" pattern
- Agent stays simple (just generates text)
- Easy to upgrade to structured output later

---

## 📊 Pattern: NoSQL Schema Design for Agents

**SQL mindset:** Normalize data, use joins
**NoSQL mindset:** Denormalize, optimize for queries

### Design Process

**Step 1: Identify Query Patterns**
```
What questions will the agent ask?
1. "What venues were suggested in the last 30 days?"
2. "Show me all recommendations with weather conditions"
3. (Future) "What events at Columbus Zoo were recommended?"
```

**Step 2: Design Schema Around Queries**
```python
# Query 1: Time-range lookup
# Need: Indexed timestamp field
{
  "timestamp": datetime,  # ← Firestore auto-indexes this
  "venues_mentioned": ["Zoo", "Park"]
}

# Query 2: Filter by weather
# Need: Weather as searchable field
{
  "timestamp": datetime,
  "weather_conditions": "Sunny, 72°F",  # ← Can query this
  "venues_mentioned": [...]
}
```

**Step 3: Denormalize for Performance**
```python
# ❌ BAD (SQL thinking): Separate collections
Collection: recommendations
  - id, timestamp, weather

Collection: venues
  - recommendation_id, venue_name

# Requires: Load recommendation, then query venues (2 reads)

# ✅ GOOD (NoSQL thinking): Embed venues
Collection: recommendations
  - timestamp
  - venues_mentioned: ["Zoo", "Park"]  # ← Array field
  - raw_suggestions: "Full text..."

# Requires: Single document read
```

### Our Schema

```python
{
  "timestamp": datetime,        # For time-range queries
  "date": "2025-12-26",        # Human-readable
  "venues_mentioned": [...],   # Denormalized (embedded)
  "events_mentioned": [...],   # Optional nested data
  "weather_conditions": str,   # Context for future ML
  "raw_suggestions": str,      # Full text (for reprocessing)
  "created_by": "v1"          # Versioning for schema changes
}
```

**Why include `raw_suggestions`?**
- Can reprocess later with better extraction logic
- Debugging (see exactly what agent said)
- Audit trail (compliance, review)

**Why include `created_by` version?**
- Schema evolution (v1 → v2 migration)
- A/B testing different agents
- Rollback capability

---

## 🎯 Pattern: Materialized Views

**Problem:** Database has rich data, but agent only needs a summary.

**Anti-pattern:**
```python
# Load ALL recommendation data
recommendations = get_recent_recommendations(days=30)

# Agent prompt with 50KB of JSON
SYSTEM_PROMPT = f"""
Recent history: {json.dumps(recommendations, indent=2)}
...
"""
```

**Issues:**
- Wastes tokens (costs money)
- Slower (more tokens to process)
- Context window pollution

**Better: Materialized View**
```python
def get_recently_visited_venues(days: int = 30) -> List[str]:
    """
    Materialized view pattern:
    - Query database for full documents
    - Extract only what agent needs (venue names)
    - Return minimal data
    """
    recommendations = get_recent_recommendations(days)

    # Materialize: Reduce rich data to just venue names
    venues = set()
    for rec in recommendations:
        venues.update(rec.get('venues_mentioned', []))

    return sorted(list(venues))

# Agent prompt with <1KB of data
venues = get_recently_visited_venues()
SYSTEM_PROMPT = f"Recently visited: {', '.join(venues)}"
```

**Benefits:**
- ✅ 50x smaller context (50KB → 1KB)
- ✅ Faster inference
- ✅ Lower costs
- ✅ More focused agent (less distraction)

**When to send full data:**
- User asks for details: "What did we do at the zoo last time?"
- Agent needs reasoning: "Why did we enjoy that venue?"

---

## 🔐 Pattern: Credential Management

**3 Layers of Security:**

### 1. Development (Your Laptop)
```bash
# .env file (gitignored!)
GOOGLE_APPLICATION_CREDENTIALS=./credentials/firebase-credentials.json

# .gitignore
credentials/
*.json
```

### 2. CI/CD (GitHub Actions)
```yaml
# Stored as GitHub Secret
- name: Authenticate
  uses: google-github-actions/auth@v1
  with:
    credentials_json: ${{ secrets.GCP_CREDENTIALS }}
```

### 3. Production (Cloud Run / GKE)
```yaml
# Use Workload Identity (no JSON files!)
# GCP automatically injects credentials
# No manual key management
```

**Our Implementation:**
```python
# recommendation_db.py
creds_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
if not creds_path:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set")

credentials = service_account.Credentials.from_service_account_file(creds_path)
db = firestore.Client(credentials=credentials)
```

**Principle:** Fail fast if credentials missing. Don't silently fall back to broken state.

---

## 📈 Performance Optimization Patterns

### 1. Connection Pooling (Singleton Pattern)
```python
# ❌ BAD: New connection per call
def get_venues():
    db = firestore.Client()  # Expensive! (100ms+ auth)
    return db.collection('recs').get()

# ✅ GOOD: Reuse connection
_db_instance = None

def get_db():
    global _db_instance
    if _db_instance is None:
        _db_instance = firestore.Client()  # Once per app lifecycle
    return _db_instance
```

### 2. Lazy Loading
```python
# Only load database when actually needed
class RecommendationDatabase:
    def __init__(self):
        # Don't connect here
        self._client = None

    @property
    def db(self):
        if self._client is None:
            self._client = firestore.Client()  # Connect on first use
        return self._client
```

### 3. Batch Operations (Future Enhancement)
```python
# If saving multiple recommendations
batch = db.batch()
for rec in recommendations:
    ref = db.collection('recs').document()
    batch.set(ref, rec)
batch.commit()  # One network call instead of N
```

---

## 🧪 Testing State Management

### Unit Tests - Mock External State
```python
from unittest.mock import patch

def test_agent_with_mocked_venues():
    with patch('recommendation_db.get_recently_visited_venues') as mock:
        mock.return_value = ["Columbus Zoo", "Metro Parks"]

        state = create_messages({})
        assert "Columbus Zoo" in state['messages'][0]['content']
```

### Integration Tests - Use Test Database
```python
@pytest.fixture
def test_db():
    """Use separate Firestore collection for tests"""
    os.environ['FIRESTORE_COLLECTION_PREFIX'] = 'test'
    yield
    # Cleanup: Delete test data
```

### E2E Tests - Real Database (Sparingly)
```python
@pytest.mark.slow
@pytest.mark.skipif(not os.getenv('RUN_E2E_TESTS'), reason="Skip expensive tests")
def test_full_pipeline():
    """Only run manually to verify production setup"""
    graph.invoke({})
```

---

## 📚 Further Reading & Patterns to Explore

### Patterns We Used
1. ✅ Repository Pattern - `RecommendationDatabase` class
2. ✅ Facade Pattern - `get_recently_visited_venues()` convenience functions
3. ✅ Singleton Pattern - `get_db()` instance management
4. ✅ State Hydration - Pre-fetch before agent runs
5. ✅ Side-Effect Nodes - `save_recommendation_to_history`
6. ✅ Graceful Degradation - Try/except with fallbacks
7. ✅ Materialized Views - Return minimal data

### Advanced Patterns (Not Implemented Yet)

**Event Sourcing:**
```python
# Instead of storing current state, store events
Collection: events
  - {type: "venue_recommended", venue: "Zoo", timestamp: ...}
  - {type: "venue_visited", venue: "Zoo", timestamp: ...}
  - {type: "venue_rated", venue: "Zoo", rating: 5, timestamp: ...}

# Rebuild state by replaying events
def get_visited_venues():
    events = db.collection('events').where('type', '==', 'venue_visited').get()
    return [e['venue'] for e in events]
```

**CQRS (Command Query Responsibility Segregation):**
```python
# Write model (optimized for updates)
save_recommendation(...)  # → Firestore

# Read model (optimized for queries)
get_venues()  # → Redis cache (fast lookup)

# Background job: Sync Firestore → Redis
```

**Vector Embeddings for Semantic Search:**
```python
# Store embeddings for semantic queries
{
  "raw_suggestions": "Visit the zoo for animal exhibits...",
  "embedding": [0.123, 0.456, ...],  # 1536-dim vector
}

# Agent asks: "What outdoor activities did we suggest?"
query_embedding = embed("outdoor activities")
similar_recs = vector_search(query_embedding, threshold=0.8)
```

---

## 🎯 Key Takeaways

1. **Choose storage based on access patterns:**
   - Always needed → Pre-fetch (hydration)
   - Sometimes needed → Tool
   - Rarely needed → Don't load

2. **Separate agent logic from state logic:**
   - Agent: "What to recommend?"
   - State manager: "Where/how to store?"

3. **Design for failure:**
   - Graceful degradation
   - Agent should work even if DB is down

4. **Optimize for tokens:**
   - Materialized views
   - Return only what agent needs
   - Full data costs money

5. **NoSQL ≠ SQL:**
   - Denormalize for query performance
   - Embed related data
   - Design around your queries

6. **Patterns evolve:**
   - Start simple (JSON file)
   - Add complexity when needed (Firestore)
   - Don't over-engineer

---

## Questions to Ask When Designing State

1. **Lifetime:** How long does this data live?
2. **Scope:** Who can access this data?
3. **Frequency:** How often is it accessed?
4. **Size:** How big is it?
5. **Latency:** How fast must queries be?
6. **Consistency:** How fresh must it be?
7. **Failure:** What happens if unavailable?

Answers guide your pattern choice!

---

*This document reflects patterns used in family-manager as of December 2025. As the system evolves, patterns may change. The principles remain constant.*
