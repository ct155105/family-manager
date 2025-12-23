"""
Columbus Metro Parks Events Scraper

Uses AI-assisted web scraping to extract event information from Columbus Metro Parks.
Note: Metro Parks has multiple park locations around Columbus - outdoor venues.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_metroparks_events", description="Get upcoming events from Columbus Metro Parks. Multiple outdoor park locations around Columbus, various nature programs and activities.")
def get_metroparks_events() -> str:
    """
    Scrapes the Columbus Metro Parks events page using AI-assisted extraction.
    Returns events from various park locations around Columbus.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.metroparks.net/events-new/"
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
        extraction_prompt = f"""Extract all upcoming events from this Columbus Metro Parks events webpage.

For each event, extract:
- title: Event name
- date: Event date or date range
- time: Event time if available
- description: Brief description of the activity
- venue: Specific Metro Park location name
- address: Park address if available
- type: Type of activity (e.g., "Nature Program", "Hike", "Workshop", "Family Event")
- age_requirements: Any age restrictions mentioned
- cost: Pricing information (often free)
- registration: Whether registration is required

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Nature programs and guided hikes
2. Educational workshops
3. Family activities
4. Special events

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Guided Nature Hike",
    "date": "Saturday, December 28",
    "time": "10:00 AM - 12:00 PM",
    "description": "Join a naturalist for a guided hike...",
    "venue": "Battelle Darby Creek Metro Park",
    "address": "1775 Darby Creek Dr, Galloway, OH 43119",
    "type": "Nature Program",
    "age_requirements": "All ages",
    "cost": "Free",
    "registration": "Required"
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
