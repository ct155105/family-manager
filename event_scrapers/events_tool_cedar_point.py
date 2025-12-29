"""
Cedar Point Events Scraper

Uses AI-assisted web scraping to extract event information from Cedar Point.
Note: 2+ hour drive from Columbus (Sandusky, OH). Seasonal amusement park.
Best known for roller coasters - world-class thrill rides.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_cedar_point_events", description="Get events and operating info from Cedar Point amusement park in Sandusky, OH. 2+ hours from Columbus. Seasonal (May-Oct typically). Best for thrill rides, also has kids areas. Check for HalloWeekends in fall.")
def get_cedar_point_events() -> str:
    """
    Scrapes Cedar Point events page using AI-assisted extraction.
    Returns special events, operating calendar, and seasonal offerings.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.cedarpoint.com/events"
    print(f"Fetching events from {url}...")

    try:
        # Load webpage content
        loader = WebBaseLoader(url)
        docs = loader.load()

        if not docs or len(docs) == 0:
            return json.dumps({"error": "Failed to load webpage content"})

        page_content = docs[0].page_content

        # Initialize LLM for extraction
        llm = init_chat_model(
            model="gpt-4o-mini",
            model_provider="openai",
            temperature=0
        )

        # Prompt for structured data extraction
        extraction_prompt = f"""Extract all upcoming events and operating information from this Cedar Point webpage.

For each event or operating period, extract:
- title: Event name or operating period
- date: Event dates or operating dates
- time: Park hours if mentioned
- description: Brief description of what's special about this event/period
- type: Type (e.g., "Seasonal Event", "Special Event", "Operating Calendar", "Concert", "Festival")
- age_requirements: Any age/height notes for the event
- cost: Ticket prices if mentioned, or "Park admission required"
- venue: Always "Cedar Point"
- address: Always "1 Cedar Point Dr, Sandusky, OH 44870"
- notes: Important details (reservations, weather, parking, what's included)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Current operating status (is the park open?)
2. Special events (HalloWeekends, WinterFest, etc.)
3. Live entertainment and shows
4. New rides or attractions for the season
5. Family-friendly events
6. Concert series or special performances

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "HalloWeekends",
    "date": "Sep 13 - Oct 27, 2025",
    "time": "6:00 PM - Midnight (Fri-Sun)",
    "description": "Haunted houses, scare zones, and Halloween theming throughout the park...",
    "type": "Seasonal Event",
    "age_requirements": "Some haunted houses not suitable for young children",
    "cost": "Park admission required",
    "venue": "Cedar Point",
    "address": "1 Cedar Point Dr, Sandusky, OH 44870",
    "notes": "Not recommended for children under 13 after dark"
  }}
]
"""

        # Get structured response from LLM
        response = llm.invoke(extraction_prompt)

        # Extract content from response
        if hasattr(response, 'content'):
            result = response.content
        else:
            result = str(response)

        # Clean up markdown code blocks if present
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        result = result.strip()

        # Validate it's valid JSON
        try:
            events = json.loads(result)
            if not isinstance(events, list):
                return json.dumps({"error": "Extracted data is not a list of events"})
            return json.dumps(events, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Failed to parse extracted events as JSON: {str(e)}", "raw_response": result})

    except Exception as e:
        return json.dumps({"error": f"Failed to fetch or process events: {str(e)}"})
