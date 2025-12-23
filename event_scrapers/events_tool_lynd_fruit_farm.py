"""
Lynd Fruit Farm Events Scraper

Uses AI-assisted web scraping to extract event information from Lynd Fruit Farm.
Note: Outdoor farm with seasonal activities (apple picking, pumpkin patch, etc.).
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_lynd_fruit_farm_events", description="Get upcoming events from Lynd Fruit Farm. Outdoor farm with seasonal activities like apple picking, pumpkin patch, hayrides, and family events.")
def get_lynd_fruit_farm_events() -> str:
    """
    Scrapes the Lynd Fruit Farm events page using AI-assisted extraction.
    Returns seasonal activities and special events at the farm.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://lyndfruitfarm.com/events-and-activities"
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
        extraction_prompt = f"""Extract all upcoming events and seasonal activities from this Lynd Fruit Farm webpage.

For each event or activity, extract:
- title: Event or activity name
- date: Event date or date range (or "Seasonal" if ongoing)
- time: Event time or operating hours
- description: Brief description of the activity
- type: Type of activity (e.g., "Seasonal Activity", "Special Event", "Farm Experience", "Family Activity")
- age_requirements: Any age restrictions mentioned
- cost: Pricing information if available
- venue: Always "Lynd Fruit Farm"
- address: Always "9394 Morse Rd, Pataskala, OH 43062"
- seasonal_notes: When this activity is available (e.g., "Fall only", "September-October")

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Seasonal activities (apple picking, pumpkin patch, etc.)
2. Special events (festivals, themed weekends)
3. Farm experiences (hayrides, corn maze, etc.)
4. Educational programs

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Apple Picking",
    "date": "Seasonal",
    "time": "9:00 AM - 6:00 PM",
    "description": "Pick your own apples from our orchards...",
    "type": "Seasonal Activity",
    "age_requirements": "All ages",
    "cost": "Pay by the pound",
    "venue": "Lynd Fruit Farm",
    "address": "9394 Morse Rd, Pataskala, OH 43062",
    "seasonal_notes": "September - October, weather permitting"
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
