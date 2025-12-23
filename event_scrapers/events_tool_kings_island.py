"""
Kings Island Events Scraper

Uses AI-assisted web scraping to extract event information from Kings Island.
Note: 1h 45min from Columbus - seasonal operation, weather-dependent.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_kings_island_events", description="Get events from Kings Island amusement park. 1h 45min from Columbus, seasonal operation, special events like Halloween Haunt and WinterFest.")
def get_kings_island_events() -> str:
    """
    Scrapes Kings Island events page using AI-assisted extraction.
    Returns operating calendar, special events, and seasonal offerings.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.visitkingsisland.com/events"
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
        extraction_prompt = f"""Extract upcoming events and operating information from this Kings Island webpage.

For each event or operating period, extract:
- title: Event name
- date: Event dates or operating dates
- time: Operating hours if specified
- description: Event description
- type: Type (e.g., "Seasonal Event", "Operating Calendar", "Special Event", "Holiday Event")
- age_requirements: Any height/age requirements for rides if mentioned
- cost: Ticket pricing if mentioned
- venue: Always "Kings Island"
- address: Always "6300 Kings Island Dr, Mason, OH 45040"
- notes: Important details (weather-dependent, seasonal, height requirements, reservations, etc.)

Return ONLY a valid JSON array. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Special seasonal events (Halloween Haunt, WinterFest, etc.)
2. Operating calendar/schedule
3. Special shows or entertainment
4. New rides or attractions

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Halloween Haunt",
    "date": "Select nights September - October",
    "time": "7:00 PM - 1:00 AM",
    "description": "Haunted mazes, scare zones...",
    "type": "Seasonal Event",
    "age_requirements": "Not recommended for children under 13",
    "cost": "Separate ticket or season pass",
    "venue": "Kings Island",
    "address": "6300 Kings Island Dr, Mason, OH 45040",
    "notes": "Seasonal - fall only. Weather permitting."
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
