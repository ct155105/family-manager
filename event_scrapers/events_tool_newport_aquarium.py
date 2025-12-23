"""
Newport Aquarium Events Scraper

Uses AI-assisted web scraping to extract event information from Newport Aquarium.
Note: 2 hours from Columbus (near Cincinnati) - indoor venue, good for any weather.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_newport_aquarium_events", description="Get events from Newport Aquarium near Cincinnati. 2 hours from Columbus, indoor venue with animal encounters and exhibits.")
def get_newport_aquarium_events() -> str:
    """
    Scrapes Newport Aquarium events page using AI-assisted extraction.
    Returns animal encounters, special exhibits, and programs.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.newportaquarium.com/events"
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
        extraction_prompt = f"""Extract all upcoming events and experiences from this Newport Aquarium webpage.

For each event or experience, extract:
- title: Event/encounter name
- date: Event date or "Daily" if ongoing
- time: Time if specified
- description: What visitors can experience
- type: Type (e.g., "Animal Encounter", "Special Event", "Exhibit", "Show")
- age_requirements: Any age/height requirements
- cost: Pricing if mentioned (often additional fee beyond admission)
- venue: Always "Newport Aquarium"
- address: Always "1 Levee Way, Newport, KY 41071"
- notes: Important details (reservations required, weather-dependent, etc.)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Animal encounters and interactions
2. Special exhibits
3. Shows and presentations
4. Special events

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Shark Bridge",
    "date": "Daily",
    "time": "During operating hours",
    "description": "Walk across a rope bridge over shark tank...",
    "type": "Exhibit",
    "age_requirements": "",
    "cost": "Included with admission",
    "venue": "Newport Aquarium",
    "address": "1 Levee Way, Newport, KY 41071",
    "notes": "Indoor exhibit"
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
