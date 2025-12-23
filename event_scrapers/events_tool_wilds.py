"""
The Wilds Events Scraper

Uses AI-assisted web scraping to extract event information from The Wilds.
Note: 1.5 hour drive from Columbus - best for full-day trips. Seasonal operation.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_wilds_events", description="Get upcoming events and safari tours from The Wilds conservation center. Located 1.5 hours from Columbus, best for full-day trips.")
def get_wilds_events() -> str:
    """
    Scrapes The Wilds events page using AI-assisted extraction.
    Returns safari tours, special events, and seasonal offerings.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://thewilds.org/events/"
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
        extraction_prompt = f"""Extract all upcoming events and programs from The Wilds events webpage.

For each event, extract:
- title: Event or program name (e.g., "Open-Air Safari Tour", "Zipline Safari", special event names)
- date: Event date or date range
- time: Event time if available
- description: Brief description including what's included
- type: Type of activity (e.g., "Safari Tour", "Zipline Adventure", "Special Event", "Educational Program")
- age_requirements: Any age or height requirements mentioned
- cost: Pricing information if available
- duration: How long the activity takes
- venue: Always "The Wilds"
- address: Always "14000 International Rd, Cumberland, OH 43732"
- notes: Important information (seasonal availability, reservations required, etc.)

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Safari tours and experiences
2. Zipline and adventure activities
3. Special events
4. Educational programs

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Open-Air Safari Tour",
    "date": "Daily through October",
    "time": "Various times",
    "description": "2-hour guided tour...",
    "type": "Safari Tour",
    "age_requirements": "",
    "cost": "$30 adult, $20 child",
    "duration": "2 hours",
    "venue": "The Wilds",
    "address": "14000 International Rd, Cumberland, OH 43732",
    "notes": "Reservations required. Seasonal operation."
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
