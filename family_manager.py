from dotenv import load_dotenv
load_dotenv()

from typing import Annotated

from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent

class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    input_prompt: str
    html: str
    raw_message: str
    


graph_builder = StateGraph(State)

import os
from langchain.chat_models import init_chat_model

from weather_forecaster import get_weekend_forecast
from event_scrapers import (
    # Legacy scrapers
    get_metroparks_events,
    get_zoo_events,
    get_lynd_fruit_farm_events,
    # AI-assisted Priority 1 (Columbus area)
    get_conservatory_events,
    get_olentangy_caverns_info,
    get_wilds_events,
    # AI-assisted Priority 2 (Regional)
    get_cincinnati_zoo_events,
    get_newport_aquarium_events,
    get_airforce_museum_events,
    get_kings_island_events,
    get_hocking_hills_info,
)
from email_client import gmail_send_message, gmail_create_draft
from family_config import get_children_age_string, get_children_interests_string
from recommendation_db import get_recently_visited_venues, save_recommendation
from datetime import datetime, timedelta
from langchain_core.tools import tool
import json
import re

# Note: get_today_date and get_weekend_forecast are no longer tools
# They are called directly in create_messages() to pre-fetch context
# This is more efficient than having the agent decide whether to call them

tools = [
    # Legacy scrapers
    get_metroparks_events,
    get_zoo_events,
    get_lynd_fruit_farm_events,
    # AI-assisted Priority 1 (Columbus area)
    get_conservatory_events,
    get_olentangy_caverns_info,
    get_wilds_events,
    # AI-assisted Priority 2 (Regional: 1-2 hour drive)
    get_cincinnati_zoo_events,
    get_newport_aquarium_events,
    get_airforce_museum_events,
    get_kings_island_events,
    get_hocking_hills_info,
]

max_iterations = 15  # Increased from 5 to accommodate all 11 event scrapers
recursion_limit = 2 * max_iterations + 1  # LangGraph requirement: 2 * max_iterations + 1

# Main agent for activity recommendations (needs reasoning + tools)
agent = create_react_agent(
    model="openai:gpt-5.2",
    tools=tools,
)

# Model for HTML formatting (no reasoning or tools needed, but uses gpt-5.2 for quality)
html_formatter = init_chat_model(
    model="gpt-5.2",
    model_provider="openai",
    temperature=0.7  # Higher temperature for more creative/polished HTML formatting
)

def create_messages(state: State) -> list:
    """
    Creates messages with all necessary context pre-fetched.

    Context is gathered here rather than via tools because:
    - Weather is needed for 100% of executions
    - Single location (Columbus, OH), single timeframe per run
    - No multi-turn conversation in current design
    - Faster, cheaper, more reliable than tool calls
    - Agent can't forget to check critical context

    This approach follows the "Static Context vs. Dynamic Actions" pattern:
    - Static context (pre-fetched): weather, date, children's ages, interests
    - Dynamic actions (tools): event fetching based on agent's decision
    """
    # Pre-fetch all required context
    age_string = get_children_age_string()
    interests_string = get_children_interests_string()
    # Note: get_weekend_forecast is a @tool-decorated function
    # We call .invoke() to execute it as a regular function
    weather_forecast = get_weekend_forecast.invoke({})
    today = datetime.now().strftime('%Y-%m-%d')

    # Pre-fetch recommendation history (State Hydration Pattern)
    # Pattern: Load state before agent runs, not via tool
    # Why: We ALWAYS need this (100% of runs), keeps agent focused
    try:
        recently_visited = get_recently_visited_venues(days=30)
        if recently_visited:
            recent_venues_text = f"\n\nRECENT ACTIVITY HISTORY (last 30 days):\nYou recently suggested these venues: {', '.join(recently_visited)}\nPlease suggest DIFFERENT venues this time to keep activities fresh and exciting.\n"
        else:
            recent_venues_text = ""
    except Exception as e:
        # Graceful degradation: If database unavailable, continue without history
        print(f"⚠️  Could not load recommendation history: {e}")
        recent_venues_text = ""

    SYSTEM_PROMPT = f"""You are a family weekend planning assistant for Columbus, OH.

CONTEXT:
- Today's date: {today}
- Children (bedtime: 8pm):
{interests_string}

WEATHER FORECAST:
{weather_forecast}{recent_venues_text}

TASK:
Based on the weather above, suggest 3 family-friendly weekend activities.

AVAILABLE VENUES (check for events using your tools):

Columbus Area (< 1 hour):
- Columbus Metro Parks (outdoor, various locations)
- Columbus Zoo and Aquarium (mostly outdoor, some indoor areas)
- Lynd Fruit Farm (outdoor, seasonal activities)
- Franklin Park Conservatory (indoor conservatory + outdoor gardens, good rain backup)
- Olentangy Caverns (cave tours, 54°F year-round)

Regional Attractions (1-2 hours):
- The Wilds (1.5 hours, safari tours - full-day trip)
- National Museum of the US Air Force (Dayton, 1 hour, FREE admission, indoor + IMAX)
- Hocking Hills State Park (1 hour, hiking/waterfalls, highly weather-dependent)
- Cincinnati Zoo (1h 45min, Festival of Lights in winter)
- Newport Aquarium (2 hours near Cincinnati, indoor, animal encounters)
- Kings Island (1h 45min, amusement park, seasonal operation)

Ensure activities are appropriate for the children's ages, interests, and weather conditions.
Prioritize closer venues for short trips. Regional venues work best for full-day excursions.
If weather is unsuitable for outdoor activities, suggest indoor venues (Conservatory, Air Force Museum, Newport Aquarium).
"""

    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Please suggest activities for this weekend."},
        ]
    }

def get_ideas_for_today(state: State) -> str:
    """
    Returns a string with ideas for activities based on the current weather and events.
    This function is called by the agent to generate activity suggestions.
    """
    msg = agent.invoke({"messages":state["messages"], recursion_limit: recursion_limit})
    return {"raw_message": msg["messages"][-1].content}


def save_recommendation_to_history(state: State) -> dict:
    """
    Extracts venues from recommendations and saves to Firestore.

    Pattern: Post-Processing Agent Output
    - Agent generates free-form text
    - We extract structured data with a quick LLM call
    - Save structured data to database

    Teaching Note: Why not use structured output in the main agent?
    - Separation of concerns: Agent focuses on recommendations, this node handles persistence
    - Easier to test/debug separately
    - Can be disabled without changing agent
    - Alternative: Use function calling for structured output (better for production)

    Returns: Empty dict (pass-through node, doesn't modify state)
    """
    raw_message = state.get("raw_message", "")

    if not raw_message:
        print("⚠️  No recommendations to save")
        return {}

    # Pattern: Extract structured data from unstructured text using LLM
    # This is a "cheap" LLM call (small prompt, simple task)
    try:
        # Use a lightweight model for extraction (fast, cheap)
        extractor = init_chat_model(model="gpt-4o-mini", temperature=0)

        extraction_prompt = f"""Extract venue names from these family activity recommendations.

Return ONLY a JSON array of venue names mentioned, nothing else.
Example: ["Columbus Zoo", "Franklin Park Conservatory"]

Recommendations:
{raw_message}

JSON array of venues:"""

        response = extractor.invoke([{"role": "user", "content": extraction_prompt}])
        venues_text = response.content.strip()

        # Clean up markdown code blocks if present
        if venues_text.startswith('```'):
            venues_text = re.sub(r'```json\s*|\s*```', '', venues_text).strip()

        venues_mentioned = json.loads(venues_text)

        # Get weather for context
        weather_forecast = get_weekend_forecast.invoke({})

        # Save to Firestore
        doc_id = save_recommendation(
            raw_suggestions=raw_message,
            venues_mentioned=venues_mentioned,
            weather_conditions=weather_forecast[:200]  # Truncate for storage
        )

        print(f"💾 Saved recommendation history: {len(venues_mentioned)} venues")

    except Exception as e:
        # Graceful degradation: Don't fail the whole pipeline if save fails
        print(f"⚠️  Could not save recommendation history: {e}")
        print("    (Continuing anyway - recommendations still generated)")

    # Return empty dict - this is a pass-through node
    # State flows through unchanged
    return {}

def generate_newsletter_html(state: State) -> dict:
    """
    Uses gpt-5.2 via direct call to turn the raw_message into HTML suitable for a family newsletter.
    This is a simple text transformation task that doesn't require the ReAct agent or tools.

    Using gpt-5.2 with direct call (no ReAct agent) provides:
    - Faster response times (no ReAct loop overhead)
    - Cleaner architecture (no unnecessary 11 event scraper tools in context)
    - Same model quality as main agent, but more efficient for formatting tasks
    - Temperature=0.7 enables creative/polished HTML with colors, sections, styling

    Returns a dict with the generated HTML under the 'html' key.
    """
    system_prompt = (
        "You are a helpful assistant that formats family activity suggestions into a beautiful, family-friendly HTML newsletter. "
        "Use clear headings, bullet points, and highlight weather and event details. "
        "Make the newsletter visually appealing and easy to read for parents. "
        "Do not include any code blocks or markdown, just return the HTML."
    )
    user_prompt = f"Here are the activity suggestions for the family newsletter:\n\n{state['raw_message']}\n\nPlease format this as a beautiful HTML newsletter."

    # Direct LLM call - no agent, no tools needed for simple formatting
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    response = html_formatter.invoke(messages)
    html_response = response.content if hasattr(response, 'content') else str(response)
    return {"html": html_response}


def create_gmail_draft_from_html(state: State) -> dict:
    """
    Calls gmail_create_draft to create a draft email with the generated newsletter HTML.
    """
    subject = f"Teuschler Family Assistent - {datetime.now().strftime('%Y-%m-%d')}"
    to = "christeuschler@gmail.com, lpisciotta@gmail.com"
    body = state.get("raw_message", "")
    html = state.get("html", "")
    draft = gmail_create_draft(to=to, subject=subject, body=body, html=html)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("create_messages", create_messages)
graph_builder.add_node("get_ideas_for_today", get_ideas_for_today)
graph_builder.add_node("save_recommendation_to_history", save_recommendation_to_history)
graph_builder.add_node("generate_newsletter_html", generate_newsletter_html)
graph_builder.add_node("create_gmail_draft_from_html", create_gmail_draft_from_html)

# Graph flow (Teaching: Linear pipeline with side-effect node)
# START → create_messages → get_ideas → save_history → generate_html → create_draft
# The save_history node is a "side-effect node" - doesn't modify state, just persists it
graph_builder.add_edge(START, "create_messages")
graph_builder.add_edge("create_messages", "get_ideas_for_today")
graph_builder.add_edge("get_ideas_for_today", "save_recommendation_to_history")
graph_builder.add_edge("save_recommendation_to_history", "generate_newsletter_html")
graph_builder.add_edge("generate_newsletter_html", "create_gmail_draft_from_html")

graph = graph_builder.compile()
print(graph.get_graph().draw_mermaid())

state = graph.invoke({})
print("Generated HTML for family newsletter:")


# def stream_graph_updates(user_input: str):
#     for event in graph.stream({
#         "messages": [
#             {"role": "system", "content": SYSTEM_PROMPT},
#             {"role": "user", "content": user_input}
#         ]
#     }):
#         for value in event.values():
#             print("Assistant:", value["messages"][-1].content)

# while True:
#     try:
#         user_input = input("User: ")
#         if user_input.lower() in ["quit", "exit", "q"]:
#             print("Goodbye!")
#             break
#         stream_graph_updates(user_input)
#     except:
#         print("An error occurred.")
#         # exit the loop on error
#         break
