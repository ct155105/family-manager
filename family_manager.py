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


graph_builder = StateGraph(State)

import os
from langchain.chat_models import init_chat_model

from weather_forecaster import get_weekend_forecast
from events_tool_metroparks import get_metroparks_events
from events_tool_zoo import get_zoo_events
from datetime import datetime
from langchain_core.tools import tool

@tool("get_today_date", description="Get today's date in YYYY-MM-DD format.")
def get_today_date() -> str:
    """
    Returns today's date in YYYY-MM-DD format.
    """
    return datetime.now().strftime('%Y-%m-%d')

tools = [get_weekend_forecast, get_metroparks_events, get_today_date, get_zoo_events]

llm = init_chat_model("openai:gpt-4.1")
llm_with_tools = llm.bind_tools(tools)

def chatbot(state: State):
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

agent = create_react_agent(
    model="openai:gpt-4.1",
    tools=tools,
)

# The first argument is the unique node name
# The second argument is the function or object that will be called whenever
# the node is used.
graph_builder.add_node("chatbot", agent)

graph_builder.add_edge(START, "chatbot")

graph = graph_builder.compile()

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

def stream_graph_updates(user_input: str):
    for event in graph.stream({
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_input}
        ]
    }):
        for value in event.values():
            print("Assistant:", value["messages"][-1].content)

while True:
    try:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        stream_graph_updates(user_input)
    except:
        print("An error occurred.")
        # exit the loop on error
        break
