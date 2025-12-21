# AI Agent Improvements

## Overview
Enhance the AI agent's recommendation logic to provide more relevant, diverse, and personalized suggestions.

## Current State

### Agent Configuration
- **Model:** `gpt-5.2` (updated from gpt-4.1)
- **Framework:** LangGraph with ReAct agent
- **Tools:** Weather, Metro Parks events, Zoo events, Lynd Fruit Farm events, today's date
- **Max Iterations:** 5
- **Recursion Limit:** 11

### Current System Prompt
```python
SYSTEM_PROMPT = (
    "You are a helpful family weekend planning assistant. "
    "The family has 3 children, ages 3, 5, and 7. The kids go to bed at 8. "
    "Always ensure that any recommendations for plans take into account the weather forecast, "
    "and only suggest activities that are suitable for the expected weather conditions. "
    "If the user asks for a plan, check the weather first and mention it in your response. "
    "Check for events in the Columbus Metro Parks and suggest them if they are suitable for the weather. "
    "Check for events at the Columbus Zoo and suggest them if they are suitable for the weather. "
    "Check for events at Lynd Fruit Farm and suggest them if they are suitable for the weather. "
    "If the weather is not suitable for outdoor activities, suggest indoor alternatives. "
    "Recommend no more than 3 activities per day, and ensure they are family-friendly. "
    "Recommend other activites around the Columbus area that are suitable for the weather. "
)
```

---

## Task 14: Use Recommendation History

**Status:** Not Started  
**Dependencies:** Task #13 (Firestore integration)  
**Priority:** Medium

### Objective
Enable the AI to avoid suggesting recently visited venues or repeated recommendations.

### Implementation

1. **Add History Retrieval Tool:**
```python
from langchain_core.tools import tool

@tool("get_recent_recommendations")
def get_recent_recommendations(days: int = 30) -> str:
    """
    Retrieves recommendations from the last N days to avoid repeating suggestions.
    Returns a summary of recently recommended venues and events.
    """
    from database.firestore_client import get_recommendations_since
    from datetime import datetime, timedelta
    
    cutoff = datetime.now() - timedelta(days=days)
    recent = get_recommendations_since(cutoff)
    
    if not recent:
        return "No recent recommendations found."
    
    venues = set()
    events = set()
    
    for rec in recent:
        venues.update(rec.get('venues', []))
        events.update(rec.get('events', []))
    
    return json.dumps({
        'recently_visited_venues': list(venues),
        'recently_attended_events': list(events),
        'recommendation_count': len(recent)
    }, indent=2)
```

2. **Update System Prompt:**
```python
SYSTEM_PROMPT = (
    # ... existing prompt ...
    "Before making recommendations, check the recent recommendation history "
    "to avoid suggesting places the family has recently visited. "
    "Prioritize NEW and DIFFERENT experiences when possible. "
    "If a venue was recommended in the last 2 weeks, choose alternatives unless "
    "there's a compelling new event or reason to revisit. "
)
```

3. **Add Tool to Agent:**
```python
tools = [
    get_weekend_forecast,
    get_today_date,
    get_recent_recommendations,  # NEW
    # ... event tools ...
]
```

---

## Task 15: Top 3 Recommendations Logic

**Status:** Not Started  
**Priority:** High

### Objective
Ensure AI consistently provides exactly 3 well-reasoned recommendations ranked by suitability.

### Current Issues
- Sometimes provides more or fewer than 3 suggestions
- Ranking/prioritization not always clear
- Reasoning for selections could be more explicit

### Enhanced System Prompt

```python
SYSTEM_PROMPT = (
    "You are a helpful family weekend planning assistant. "
    
    # Family Context
    f"The family has {len(CHILDREN)} children, ages {get_ages_string()}. "
    f"Children's interests: {get_interests_string()}. "
    "The kids go to bed at 8 PM. "
    
    # Weather-First Approach
    "ALWAYS check the weather forecast FIRST before making any recommendations. "
    "Weather is the PRIMARY factor in determining suitable activities. "
    
    # Decision Process
    "Follow this decision process:\n"
    "1. Get today's date and weather forecast\n"
    "2. Check recent recommendation history to avoid repeats\n"
    "3. Query ALL available event tools for today's events\n"
    "4. Evaluate each option based on:\n"
    "   - Weather suitability (indoor vs outdoor)\n"
    "   - Age appropriateness for children ages {ages}\n"
    "   - Children's interests alignment\n"
    "   - Novelty (haven't visited recently)\n"
    "   - Practical factors (distance, time, cost)\n"
    "5. Select EXACTLY 3 activities and rank them 1-3\n"
    
    # Output Format
    "For each recommendation, provide:\n"
    "- Ranking (#1, #2, #3)\n"
    "- Activity name and venue\n"
    "- Why it's suitable (weather, ages, interests)\n"
    "- Practical details (time, location, cost if known)\n"
    "- Any special considerations\n"
    
    # Quality Standards
    "Recommendations must:\n"
    "- Be appropriate for the day's weather\n"
    "- Suit ALL children's ages (no activities too young or too old)\n"
    "- Align with at least one child's interests when possible\n"
    "- Be different from recent recommendations\n"
    "- Be realistic for a single day (timing, energy level)\n"
)
```

### Structured Output

Add a tool for the agent to use when finalizing recommendations:

```python
@tool("finalize_recommendations")
def finalize_recommendations(
    recommendation_1: str,
    recommendation_2: str, 
    recommendation_3: str,
    weather_summary: str
) -> str:
    """
    Save the final 3 recommendations to the database and return confirmation.
    
    Args:
        recommendation_1: Top recommendation with full details
        recommendation_2: Second recommendation with full details
        recommendation_3: Third recommendation with full details
        weather_summary: Brief weather summary for the day
    """
    from database.firestore_client import save_recommendations
    
    save_recommendations({
        'date': datetime.now(),
        'weather': weather_summary,
        'recommendations': [
            {'rank': 1, 'details': recommendation_1},
            {'rank': 2, 'details': recommendation_2},
            {'rank': 3, 'details': recommendation_3}
        ]
    })
    
    return "Recommendations saved successfully!"
```

---

## Additional Improvements

### A. Better Tool Descriptions

Update tool descriptions to help AI understand when to use each:

```python
@tool(
    "get_weekend_forecast",
    description=(
        "Get detailed weather forecast for Columbus, OH for the next 3 days. "
        "Use this FIRST before making any activity recommendations. "
        "Returns temperature highs/lows and conditions (rain, clouds, etc)."
    )
)
```

### B. Reasoning Effort Configuration

For GPT-5.2, configure reasoning effort:

```python
agent = create_react_agent(
    model="openai:gpt-5.2",
    tools=tools,
    model_kwargs={
        "reasoning_effort": "medium"  # or "high" for complex decisions
    }
)
```

### C. Memory and Context

Add conversation memory to track what was asked:

```python
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()
agent = create_react_agent(
    model="openai:gpt-5.2",
    tools=tools,
    checkpointer=memory
)
```

### D. Evaluation Metrics

Track recommendation quality:
- Weather alignment score
- Age-appropriateness score
- Interest alignment score
- Diversity score (how different from recent)

---

## Testing Plan

1. **Weather Scenarios:**
   - Sunny and warm → Outdoor recommendations
   - Rainy → Indoor only
   - Cold but clear → Mix of indoor/outdoor
   - Severe weather → All indoor

2. **Interest Alignment:**
   - Track if recommendations match children's interests
   - Measure how often each child's interests are represented

3. **Diversity:**
   - Run for 30 consecutive days
   - Measure venue repetition rate
   - Target: <20% repetition in 30 days

4. **Consistency:**
   - Always returns exactly 3 recommendations
   - Always includes weather in reasoning
   - Always checks history before suggesting

---

## Future Enhancements

1. **Feedback Loop:** Let user rate recommendations to improve over time
2. **Learning:** Track which recommendations were actually chosen
3. **Seasonal Awareness:** Special handling for holidays, school breaks
4. **Budget Tracking:** Factor in family budget constraints
5. **Friend Coordination:** Suggest activities that could include friends
