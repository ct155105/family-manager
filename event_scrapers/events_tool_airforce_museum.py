"""
National Museum of the US Air Force Events Scraper

Uses AI-assisted web scraping to extract event information from the Air Force Museum.
Note: 1 hour from Columbus (Dayton) - FREE admission, indoor venue.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_airforce_museum_events", description="Get events from National Museum of the US Air Force in Dayton. 1 hour from Columbus, FREE admission, indoor venue with IMAX theater.")
def get_airforce_museum_events() -> str:
    """
    Scrapes Air Force Museum events page using AI-assisted extraction.
    Returns special events, IMAX schedule, and temporary exhibits.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.nationalmuseum.af.mil/Visit/Events/"
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
        extraction_prompt = f"""Extract all upcoming events from this National Museum of the US Air Force webpage.

For each event, extract:
- title: Event name
- date: Event date or date range
- time: Event time if specified
- description: Event description
- type: Type (e.g., "Special Event", "IMAX Film", "Temporary Exhibit", "Educational Program")
- age_requirements: Any age recommendations
- cost: "FREE" for general admission, or IMAX ticket price if applicable
- venue: Always "National Museum of the US Air Force"
- address: Always "1100 Spaatz St, Wright-Patterson AFB, OH 45433"
- notes: Important details (registration required, capacity limits, etc.)

Return ONLY a valid JSON array. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Special events and programs
2. IMAX theater schedule
3. Temporary exhibits
4. Educational programs
5. Holiday events

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "IMAX: Top Gun Maverick",
    "date": "Daily",
    "time": "2:00 PM, 5:00 PM",
    "description": "Experience the thrilling...",
    "type": "IMAX Film",
    "age_requirements": "PG-13",
    "cost": "$9 adult, $7 child",
    "venue": "National Museum of the US Air Force",
    "address": "1100 Spaatz St, Wright-Patterson AFB, OH 45433",
    "notes": "Museum admission is FREE, IMAX tickets separate"
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
