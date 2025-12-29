"""
Nationwide Arena Events Scraper

Uses AI-assisted web scraping to extract event information from Nationwide Arena.
Home of Columbus Blue Jackets hockey. Also hosts concerts, Disney on Ice,
WWE, family shows, and more. Downtown Columbus.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_nationwide_arena_events", description="Get events from Nationwide Arena in downtown Columbus. Home of Blue Jackets hockey. Also hosts concerts, Disney on Ice, WWE, Cirque du Soleil, and family shows. Great indoor venue.")
def get_nationwide_arena_events() -> str:
    """
    Scrapes Nationwide Arena events page using AI-assisted extraction.
    Returns concerts, hockey games, family shows, and other events.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.nationwidearena.com/events"
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
        extraction_prompt = f"""Extract all upcoming events from this Nationwide Arena events webpage.

For each event, extract:
- title: Event name
- date: Event date(s)
- time: Event time / doors open time
- description: Brief description of the event
- type: Type (e.g., "Hockey", "Concert", "Family Show", "WWE", "Comedy", "Disney on Ice")
- age_requirements: Age recommendations if mentioned
- cost: Ticket price range if mentioned
- venue: Always "Nationwide Arena"
- address: Always "200 W Nationwide Blvd, Columbus, OH 43215"
- notes: Important details (parking, sold out, family-friendly)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus especially on FAMILY-FRIENDLY events:
1. Columbus Blue Jackets hockey games
2. Disney on Ice and ice shows
3. Family concerts (kid-appropriate artists)
4. Cirque du Soleil and circus shows
5. WWE and wrestling events (family seating)
6. Comedy shows (if family-appropriate)
7. Monster Jam

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Columbus Blue Jackets vs Pittsburgh Penguins",
    "date": "January 20, 2025",
    "time": "7:00 PM",
    "description": "NHL hockey action as the Blue Jackets take on the Penguins...",
    "type": "Hockey",
    "age_requirements": "All ages",
    "cost": "$30 - $200",
    "venue": "Nationwide Arena",
    "address": "200 W Nationwide Blvd, Columbus, OH 43215",
    "notes": "Family section available. Parking in Arena District garages."
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
