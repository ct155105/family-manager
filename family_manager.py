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
    get_metroparks_events,
    get_zoo_events,
    get_lynd_fruit_farm_events,
)
from email_client import gmail_send_message, gmail_create_draft
from family_config import get_children_age_string, get_children_interests_string
from datetime import datetime, timedelta
from langchain_core.tools import tool

# Note: get_today_date and get_weekend_forecast are no longer tools
# They are called directly in create_messages() to pre-fetch context
# This is more efficient than having the agent decide whether to call them

tools = [get_metroparks_events, get_zoo_events, get_lynd_fruit_farm_events]

max_iterations = 5
recursion_limit = 2 * max_iterations + 1
agent = create_react_agent(
    model="openai:gpt-5.2",
    tools=tools,
    
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

    SYSTEM_PROMPT = f"""You are a family weekend planning assistant for Columbus, OH.

CONTEXT:
- Today's date: {today}
- Children (bedtime: 8pm):
{interests_string}

WEATHER FORECAST:
{weather_forecast}

TASK:
Based on the weather above, suggest 3 family-friendly weekend activities.
Check for events at Columbus Metro Parks, Columbus Zoo, and Lynd Fruit Farm.
Ensure activities are appropriate for the children's ages, interests, and weather conditions.
If weather is unsuitable for outdoor activities, prioritize indoor alternatives.
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

def generate_newsletter_html(state: State) -> dict:
    """
    Uses the AI agent to turn the raw_message into HTML suitable for a family newsletter.
    Returns a dict with the generated HTML under the 'html' key.
    """
    system_prompt = (
        "You are a helpful assistant that formats family activity suggestions into a beautiful, family-friendly HTML newsletter. "
        "Use clear headings, bullet points, and highlight weather and event details. "
        "Make the newsletter visually appealing and easy to read for parents. "
        "Do not include any code blocks or markdown, just return the HTML."
    )
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here are the activity suggestions for the family newsletter:\n\n{state['raw_message']}\n\nPlease format this as a beautiful HTML newsletter."}
    ]
    msg = agent.invoke({"messages":messages, "recursion_limit": recursion_limit})
    html_response = msg["messages"][-1].content
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
graph_builder.add_node("generate_newsletter_html", generate_newsletter_html)
graph_builder.add_node("create_gmail_draft_from_html", create_gmail_draft_from_html)

graph_builder.add_edge(START, "create_messages")
graph_builder.add_edge("create_messages", "get_ideas_for_today")
graph_builder.add_edge("get_ideas_for_today", "generate_newsletter_html")
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
