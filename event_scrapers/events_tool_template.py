"""
[Venue Name] Events Scraper Template

Uses AI-assisted web scraping to extract event information from [Venue Name].
Note: [Indoor/Outdoor, distance from Columbus, special characteristics]
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_venue_events", description="Get upcoming events from [Venue Name]. [Brief description of venue and event types].")
def get_venue_events() -> str:
    """
    Scrapes the [Venue Name] events page using AI-assisted extraction.
    Returns [what types of events/information are returned].

    Returns:
        str: JSON array of events or error message
    """
    url = "https://example.com/events"  # TODO: Update with actual URL
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
        # TODO: Customize the extraction prompt for your specific venue
        extraction_prompt = f"""Extract all upcoming events from this [Venue Name] webpage.

For each event, extract:
- title: Event name
- date: Event date or date range
- time: Event time if available
- description: Brief description
- type: Type of event (e.g., "Workshop", "Performance", "Special Event")
- age_requirements: Any age restrictions mentioned
- cost: Pricing information
- venue: Always "[Venue Name]"
- address: Always "[Full Address]"
- notes: Important details (weather-dependent, reservations required, etc.)

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. [Key event type 1]
2. [Key event type 2]
3. [Key event type 3]
4. [Key event type 4]

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Example Event",
    "date": "December 25, 2025",
    "time": "2:00 PM - 4:00 PM",
    "description": "Example event description...",
    "type": "Special Event",
    "age_requirements": "All ages",
    "cost": "Free with admission",
    "venue": "[Venue Name]",
    "address": "[Full Address]",
    "notes": "Weather permitting"
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
