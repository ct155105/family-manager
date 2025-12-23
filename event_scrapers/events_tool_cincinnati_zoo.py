"""
Cincinnati Zoo Events Scraper

Uses AI-assisted web scraping to extract event information from Cincinnati Zoo.
Note: 1h 45min drive from Columbus - best for full-day trips.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_cincinnati_zoo_events", description="Get upcoming events from Cincinnati Zoo & Botanical Garden. 1h 45min from Columbus, popular for Festival of Lights in winter.")
def get_cincinnati_zoo_events() -> str:
    """
    Scrapes Cincinnati Zoo events page using AI-assisted extraction.
    Returns special events, shows, and seasonal offerings.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://cincinnatizoo.org/events/"
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
        extraction_prompt = f"""Extract all upcoming events from this Cincinnati Zoo events webpage.

For each event, extract:
- title: Event name
- date: Event date or date range
- time: Event time if available
- description: Brief description
- type: Event type (e.g., "Animal Show", "Special Event", "Festival", "Educational Program")
- age_requirements: Any age restrictions if mentioned
- cost: "Included with admission" or specific pricing if mentioned
- venue: Always "Cincinnati Zoo & Botanical Garden"
- address: Always "3400 Vine St, Cincinnati, OH 45220"
- notes: Important info (reservations, seasonal, etc.)

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Special events and festivals (like Festival of Lights)
2. Daily animal shows and encounters
3. Special exhibits
4. Educational programs

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Festival of Lights",
    "date": "Nov 17 - Jan 5",
    "time": "5:00 PM - 9:00 PM",
    "description": "Holiday light display...",
    "type": "Seasonal Festival",
    "age_requirements": "",
    "cost": "Included with admission",
    "venue": "Cincinnati Zoo & Botanical Garden",
    "address": "3400 Vine St, Cincinnati, OH 45220",
    "notes": "Seasonal - winter months only"
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
