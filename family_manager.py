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
from events_tool_metroparks import get_metroparks_events
from events_tool_zoo import get_zoo_events
from email_client import gmail_send_message, gmail_create_draft
from datetime import datetime, timedelta
from langchain_core.tools import tool

@tool("get_today_date", description="Get today's date in YYYY-MM-DD format.")
def get_today_date() -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    date_string = datetime.now().strftime('%Y-%m-%d')
    print(f"Today's date is {date_string}")
    return date_string

tools = [get_weekend_forecast, get_metroparks_events, get_today_date, get_zoo_events]

max_iterations = 5
recursion_limit = 2 * max_iterations + 1
agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=tools,
    
)

def create_messages(state: State) -> list:
    """
    Creates a list of messages to be used by the agent.
    This function is called by the agent to generate the initial messages.
    """


    SYSTEM_PROMPT = (
        "You are a helpful family weekend planning assistant. "
        "The family has 3 children, ages 3, 5, and 7. The kids go to bed at 8. "
        "Always ensure that any recommendations for plans take into account the weather forecast, "
        "and only suggest activities that are suitable for the expected weather conditions. "
        "If the user asks for a plan, check the weather first and mention it in your response. "
        "Check for events in the Columbus Metro Parks and suggest them if they are suitable for the weather. "
        "Check for events at the Columbus Zoo and suggest them if they are suitable for the weather. "
        "If the weather is not suitable for outdoor activities, suggest indoor alternatives. "
    )
    return {
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": "Please suggest some activities for tomorrow based on the weather and events."},
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
    subject = f"Teuschler Family Assistent - {(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')}"
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
