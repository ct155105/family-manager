import requests
from bs4 import BeautifulSoup
from langchain_core.tools import tool
import json

@tool("get_metroparks_events", description="Get a list of upcoming events from Columbus Metro Parks events website.")
def get_metroparks_events() -> str:
    """
    Scrapes the Columbus Metro Parks events page for a list of upcoming events.
    Returns a formatted string with event titles and dates.
    """
    url = "https://www.metroparks.net/events-new/"
    print(f"Fetching events from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch events. Status code: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    # Find the element with aria-label containing 'List of Events'
    events_container = soup.find(attrs={"aria-label": lambda x: x and "List of Events" in x})
    if not events_container:
        return "Could not find the events container with aria-label 'List of Events'."
    # Get the inner text (no HTML tags) of the container
    events_text = events_container.get_text(separator='\n', strip=True)
    if not events_text:
        return "No events found in the container."
    
    events = []
    # Each event is in a div with class 'tribe-events-calendar-list__event-row'
    for event_row in events_container.find_all('div', class_='tribe-events-calendar-list__event-row'):
        try:
            # Date and time
            date_time_tag = event_row.find('span', class_='tribe-event-date-start')
            date_time = date_time_tag.get_text(strip=True) if date_time_tag else ''
            end_time_tag = event_row.find('span', class_='tribe-event-time')
            end_time = end_time_tag.get_text(strip=True) if end_time_tag else ''
            # Title
            title_tag = event_row.find('h3', class_='tribe-events-calendar-list__event-title')
            if title_tag:
                title_link = title_tag.find('a')
                title = title_link.get_text(strip=True) if title_link else title_tag.get_text(strip=True)
            else:
                title = ''
            # Description
            desc_tag = event_row.find('div', class_='tribe-events-calendar-list__event-description')
            description = desc_tag.get_text(separator=' ', strip=True) if desc_tag else ''
            # Venue name
            venue_tag = event_row.find('span', class_='tribe-events-calendar-list__event-venue-title')
            venue = venue_tag.get_text(strip=True) if venue_tag else ''
            # Venue address
            address_tag = event_row.find('span', class_='tribe-events-calendar-list__event-venue-address')
            address = address_tag.get_text(strip=True) if address_tag else ''
            events.append({
                'date_time': date_time,
                'end_time': end_time,
                'title': title,
                'description': description,
                'venue': venue,
                'address': address
            })
        except Exception as e:
            continue
    if not events:
        return "No structured events found."
    return json.dumps(events, indent=2)
