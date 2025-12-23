"""
Columbus Zoo and Aquarium Events Scraper

Uses AI-assisted web scraping to extract event information from Columbus Zoo.
Note: Mostly outdoor zoo with some indoor exhibits (aquarium, reptile house).
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_columbus_zoo_events", description="Get upcoming events from Columbus Zoo and Aquarium. Mostly outdoor zoo with some indoor exhibits, includes seasonal events and special programs.")
def get_zoo_events() -> str:
    """
    Scrapes the Columbus Zoo and Aquarium events page using AI-assisted extraction.
    Returns special events, seasonal programs, and animal encounters.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://columbuszoo.org/events"
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
        extraction_prompt = f"""Extract all upcoming events from this Columbus Zoo and Aquarium events webpage.

For each event, extract:
- title: Event name
- date: Event date or date range
- time: Event time if available
- description: Brief description of the event
- type: Type of event (e.g., "Seasonal Event", "Animal Encounter", "Special Program", "Educational Event")
- age_requirements: Any age restrictions mentioned
- cost: Pricing information (note if included with admission or additional fee)
- venue: Always "Columbus Zoo and Aquarium"
- address: Always "4850 Powell Rd, Powell, OH 43065"
- notes: Important details (weather-dependent, member benefits, etc.)

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Seasonal events (Wildlights, Boo at the Zoo, etc.)
2. Animal encounters and experiences
3. Educational programs
4. Special exhibits

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Wildlights",
    "date": "November 15 - January 5",
    "time": "5:00 PM - 9:00 PM",
    "description": "Holiday lights festival throughout the zoo...",
    "type": "Seasonal Event",
    "age_requirements": "All ages",
    "cost": "Included with admission",
    "venue": "Columbus Zoo and Aquarium",
    "address": "4850 Powell Rd, Powell, OH 43065",
    "notes": "Weather permitting. Members get discount."
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
