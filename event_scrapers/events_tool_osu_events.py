"""
Ohio State University Events Scraper

Uses AI-assisted web scraping to extract event information from OSU.
Covers Schottenstein Center events (concerts, Disney on Ice, family shows)
and other OSU campus events suitable for families.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_osu_events", description="Get family-friendly events at Ohio State University campus in Columbus. Includes Schottenstein Center (concerts, Disney on Ice, family shows), OSU athletics, and campus events. Great for gameday atmosphere!")
def get_osu_events() -> str:
    """
    Scrapes Schottenstein Center/OSU events using AI-assisted extraction.
    Returns concerts, family shows, and athletic events.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.schottensteincenter.com/events"
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
        extraction_prompt = f"""Extract all upcoming events from this Schottenstein Center / Ohio State events webpage.

For each event, extract:
- title: Event name
- date: Event date(s)
- time: Event time / doors open time
- description: Brief description of the event
- type: Type (e.g., "Concert", "Family Show", "Disney on Ice", "Basketball", "Hockey", "Comedy", "Wrestling")
- age_requirements: Age recommendations if mentioned
- cost: Ticket price range if mentioned
- venue: Venue name (Schottenstein Center, Ohio Stadium, etc.)
- address: Always "555 Borror Dr, Columbus, OH 43210" for Schottenstein Center
- notes: Important details (parking, family-friendly, sold out status)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus especially on FAMILY-FRIENDLY events:
1. Disney on Ice and similar ice shows
2. Kid-friendly concerts
3. Family comedy shows
4. Cirque du Soleil type performances
5. Monster Jam / WWE (if family seating available)
6. OSU Men's/Women's Basketball games
7. OSU Hockey games

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Disney on Ice: Frozen Adventures",
    "date": "January 15-19, 2025",
    "time": "Various showtimes",
    "description": "See Anna, Elsa, and friends skate through the magical world of Frozen...",
    "type": "Family Show",
    "age_requirements": "All ages - great for kids 3+",
    "cost": "$25 - $125",
    "venue": "Schottenstein Center",
    "address": "555 Borror Dr, Columbus, OH 43210",
    "notes": "Parking available in adjacent lots. Premium seats include meet & greet."
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
