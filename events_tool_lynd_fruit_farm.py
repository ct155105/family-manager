import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from langchain_core.tools import tool

@tool("get_lynd_fruit_farm_events", description="Get a list of upcoming events from Lynd Fruit Farm events website.")
def get_lynd_fruit_farm_events():
    try:
        url = "https://lyndfruitfarm.com/events-and-activities"
        print(f"Fetching events from {url}...")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        ## PARSER CODE HERE ##
        events = []
        
        # Find all event list items
        event_items = soup.find_all('div', class_='ue-event-list-item')
        
        for item in event_items:
            event_data = {
                'date_time': '',
                'end_time': '',
                'title': '',
                'description': '',
                'venue': '',
                'address': ''
            }
            
            # Extract title
            title_elem = item.find('div', class_='ue-event-list-item-details-title')
            if title_elem:
                event_data['title'] = title_elem.get_text(strip=True)
            
            # Extract venue/location
            location_elem = item.find('div', class_='ue-event-list-item-details-attributes-location')
            if location_elem:
                location_label = location_elem.find('div', class_='ue-event-list-item-details-attributes-label')
                if location_label:
                    event_data['venue'] = location_label.get_text(strip=True)
            
            # Extract date
            date_elem = item.find('div', class_='ue-event-list-item-details-attributes-date')
            date_str = ''
            if date_elem:
                date_label = date_elem.find('div', class_='ue-event-list-item-details-attributes-label--date')
                if date_label:
                    date_str = date_label.get_text(strip=True)
            
            # Extract time information
            time_elems = item.find_all('div', class_='ue-event-list-item-details-attributes-time')
            start_time = ''
            end_time = ''
            
            if time_elems:
                for i, time_elem in enumerate(time_elems):
                    time_label = time_elem.find('div', class_='ue-event-list-item-details-attributes-label')
                    if time_label:
                        time_text = time_label.get_text(strip=True)
                        if i == 0:
                            start_time = time_text
                        elif i == 1:
                            end_time = time_text
            
            # Combine date and start time
            if date_str and start_time:
                event_data['date_time'] = f"{date_str} {start_time}"
            elif date_str:
                event_data['date_time'] = date_str
            elif start_time:
                event_data['date_time'] = start_time
            
            # Set end time
            event_data['end_time'] = end_time
            
            # Extract description
            desc_elem = item.find('div', class_='ue-event-list-item-details-text')
            if desc_elem:
                # Get all text content, preserving structure
                desc_text = desc_elem.get_text(separator=' ', strip=True)
                # Clean up extra whitespace
                desc_text = re.sub(r'\s+', ' ', desc_text)
                event_data['description'] = desc_text
            
            # Address is typically not provided in this format, leaving empty
            event_data['address'] = ''
            
            events.append(event_data)
        
        return events
        
    except Exception as e:
        return f"Error: {str(e)}"
