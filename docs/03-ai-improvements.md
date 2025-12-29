# AI Agent Improvements

## Overview
Enhance the AI agent's recommendation logic to provide more relevant, diverse, and personalized suggestions.

## Current State (Updated December 2025)

### Agent Configuration
- **Model:** `gpt-5.2`
- **Framework:** LangGraph with ReAct agent
- **Tools:** 19 event scrapers (see `02-event-scrapers.md`)
- **Max Iterations:** 25
- **Recursion Limit:** 51

### Current Architecture
The system prompt is now **dynamically generated** in `create_messages()` with:
- Pre-fetched weather forecast (State Hydration Pattern)
- Dynamic children ages from `family_config.py`
- Children interests from `family_config.py`
- Recent venue history from Firestore (to avoid repetition)

See `family_manager.py:create_messages()` for the full implementation.

---

## Task 14: Use Recommendation History

**Status:** ✅ COMPLETED (2025-12-26)
**Dependencies:** Task #3 (Firestore integration)
**Priority:** Medium

### Objective
Enable the AI to avoid suggesting recently visited venues or repeated recommendations.

### What Was Implemented

We chose **State Hydration** over the tool-based approach proposed below. This is a better pattern because:
- Agent can't "forget" to check history (always in system prompt)
- Fewer LLM calls (cheaper, faster)
- 100% of runs need this data

**Implementation in `family_manager.py:create_messages()`:**
```python
# Pre-fetch recommendation history (State Hydration Pattern)
recently_visited = get_recently_visited_venues(days=30)
if recently_visited:
    recent_venues_text = f"""
RECENT ACTIVITY HISTORY (last 30 days):
You recently suggested these venues: {', '.join(recently_visited)}
Please suggest DIFFERENT venues this time to keep activities fresh and exciting.
"""

# Inject into system prompt
SYSTEM_PROMPT = f"""...{recent_venues_text}..."""
```

**Why State Hydration beats Tool-based approach:**
| Factor | State Hydration (chosen) | Tool-based (original proposal) |
|--------|--------------------------|-------------------------------|
| Reliability | Always included | Agent might forget to call |
| Cost | 1 fewer LLM call | Extra tool call |
| Latency | Faster | Slower |
| Complexity | Simpler | More code |

### Original Proposal (Not Implemented - For Reference Only)

<details>
<summary>Click to see original tool-based proposal</summary>

1. **Add History Retrieval Tool:**
```python
@tool("get_recent_recommendations")
def get_recent_recommendations(days: int = 30) -> str:
    # ... tool implementation
```

2. **Update System Prompt to mention the tool**

3. **Add Tool to Agent**
</details>

---

## Task 15: Top 3 Recommendations Logic

**Status:** ⏸️ DEFERRED (Optional Enhancement)
**Priority:** Low

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

### A. Better Tool Descriptions - ⏸️ DEFERRED

Current tool descriptions are adequate. Could be enhanced if agent makes poor tool choices.

### B. Reasoning Effort Configuration - ❌ NOT APPLICABLE

The `reasoning_effort` parameter was specific to o1 models. GPT-5.2 uses different configuration.

### C. Memory and Context - ❌ NOT NEEDED

Our application runs single-shot (one request → one newsletter). No multi-turn conversation needed.
If we add interactive chat mode in the future, revisit this.

### D. Evaluation Metrics - See `03-model-evals.md`

For tracking recommendation quality, see the dedicated model evals documentation:
- Weather alignment score
- Age-appropriateness score
- Interest alignment score
- Diversity score (how different from recent)

**Recommendation:** Implement `03-model-evals.md` before this file's remaining tasks.

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
