"""
Ohio State Fair Events Scraper

Uses AI-assisted web scraping to extract event information from Ohio State Fair.
Note: Annual fair in late July/August, runs about 12 days.
Located in Columbus at the Ohio Expo Center.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_ohio_state_fair_events", description="Get schedule and events from Ohio State Fair in Columbus. Annual event in late July/August (~12 days). Features rides, animals, concerts, food, and competitions. Located at Ohio Expo Center.")
def get_ohio_state_fair_events() -> str:
    """
    Scrapes Ohio State Fair website using AI-assisted extraction.
    Returns concert schedule, special events, and fair information.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://ohiostatefair.com/"
    print(f"Fetching information from {url}...")

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
        extraction_prompt = f"""Extract all fair information, concerts, and events from this Ohio State Fair webpage.

For each event or attraction, extract:
- title: Event or attraction name
- date: Specific dates (fair runs ~12 days in late July/August)
- time: Event time if applicable
- description: What visitors can experience
- type: Type (e.g., "Concert", "Competition", "Exhibition", "Ride Area", "Animal Show", "Fair Info")
- age_requirements: Any age notes or "All ages"
- cost: Fair admission prices or "Included with admission"
- venue: Always "Ohio State Fair"
- address: Always "717 E 17th Ave, Columbus, OH 43211 (Ohio Expo Center)"
- notes: Important details (parking, heat advisory, special tickets needed)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Fair dates and hours of operation
2. Concert lineup and schedule
3. Family-friendly attractions
4. Animal exhibits and shows
5. Rides and midway information
6. Special events and competitions
7. Food and vendor highlights

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "2025 Ohio State Fair",
    "date": "July 23 - August 3, 2025",
    "time": "10:00 AM - 10:00 PM daily",
    "description": "12 days of rides, animals, food, concerts, and Ohio pride...",
    "type": "Fair Info",
    "age_requirements": "All ages",
    "cost": "Adults $12, Seniors $10, Children (5-12) $8, Under 5 Free",
    "venue": "Ohio State Fair",
    "address": "717 E 17th Ave, Columbus, OH 43211 (Ohio Expo Center)",
    "notes": "Ride wristbands sold separately. Parking $10."
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
