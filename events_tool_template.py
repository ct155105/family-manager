import requests
from bs4 import BeautifulSoup
# from langchain_core.tools import tool
import json

# @tool("get_metroparks_events", description="Get a list of upcoming events from Columbus Metro Parks events website.")
def get_metroparks_events() -> str:
    """
    Scrapes the events page for a list of upcoming events.
    Returns a formatted string with event titles and dates.
    """
    url = "https://www.metroparks.net/events-new/"
    print(f"Fetching events from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch events. Status code: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    # Find the element with aria-label containing 'List of Events'
    
    events = []
    ## PARSER CODE HERE ##
    
    if not events:
        return "No structured events found."
    return json.dumps(events, indent=2)
