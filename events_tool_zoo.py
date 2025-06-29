from bs4 import BeautifulSoup
import requests
import json
from langchain_core.tools import tool


@tool("get_columbus_zoo_events", description="Get a list of upcoming events from Columbus Zoo and Aquarium events website.")
def get_zoo_events() -> str:
    """
    Scrapes the Columbus Zoo and Aquarium events page for a list of upcoming events.
    Returns a JSON string with event details including title, date/time, description, venue, and
    address.
    """
    
    url = "https://columbuszoo.org/events"
    print(f"Fetching events from {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch events. Status code: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    
    results = []
    
    ## PARSER CODE HERE ##
    # The relevant event listings are under:
    # <div class="views-element-container ... block-views-blockevents-block-2" ...>
    # Inside: <div class="view-content"> and each event is <div class="item">

    event_container = soup.find("div", class_="views-element-container", id="block-views-block-events-block-2")
    if not event_container:
        return results  # No events found
    
    view_content = event_container.find("div", class_="view-content")
    if not view_content:
        return results

    items = view_content.find_all("div", class_="item")
    
    # We'll use these as defaults since the events are for "Columbus Zoo and Aquarium"
    default_venue = "Columbus Zoo and Aquarium"
    default_address = "4850 Powell Rd, Powell, OH 43065"  # public address for the zoo

    for item in items:
        event = {}
        
        # 1. Title
        a_tag = item.find("a", class_="wrap")
        event['title'] = a_tag['title'].strip() if a_tag and a_tag.has_attr('title') else ''

        # 2. Date/Time / End Time
        # <h4>JUL 31 - OCT 5</h4> or other variants
        h4 = item.find("h4")
        date_text = h4.get_text(" ", strip=True) if h4 else ""
        # By default, assign everything to date_time, and split on '-' or '&'.
        # Examples: "JUN 29 & 30", "JUL 31 - OCT 5", "JUN 30 - JUL 4", "AUG 17 - 18", "WEEKENDS Oct 10 - 26"
        date_time = date_text.strip()
        end_time = ''
        import re

        # Try to split out ranges for end_time
        if '-' in date_time:
            left, right = date_time.split('-', 1)
            event['date_time'] = left.strip()
            event['end_time'] = right.strip()
        else:
            event['date_time'] = date_time
            event['end_time'] = ''
        
        # 3. Description (no dedicated field, but try to extract from img alt text or None)
        # Sometimes the logo image alt has meaningful context
        img_logo = item.find('span', class_='logo')
        description = ''
        if img_logo:
            img = img_logo.find('img')
            if img and img.has_attr('alt'):
                description = img['alt'].strip()
        event['description'] = description

        # 4. Venue (assume always Columbus Zoo and Aquarium unless info elsewhere)
        event['venue'] = default_venue

        # 5. Address (assume default)
        event['address'] = default_address

        # Add to results
        results.append(event)
    ## END PARSER CODE ##
    
    return json.dumps(results, indent=2)
