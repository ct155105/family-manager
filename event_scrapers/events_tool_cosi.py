"""
COSI (Center of Science and Industry) Events Scraper

Uses AI-assisted web scraping to extract event information from COSI.
Note: Indoor science museum in Columbus - great for any weather.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_cosi_events", description="Get upcoming events from COSI (Center of Science and Industry) in Columbus. Indoor science museum with planetarium, exhibits, and hands-on activities. Great for any weather.")
def get_cosi_events() -> str:
    """
    Scrapes COSI events page using AI-assisted extraction.
    Returns special events, exhibits, shows, and educational programs.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://cosi.org/experiences"
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
        extraction_prompt = f"""Extract all current exhibits, shows, and experiences from this COSI (Center of Science and Industry) webpage.

For each item, extract:
- title: Exhibit or experience name
- date: Availability dates or "Ongoing" if permanent
- time: Show times if applicable
- description: Brief description of what visitors can do/see
- type: Type (e.g., "Exhibit", "Planetarium Show", "Live Show", "Hands-on Activity", "Special Event")
- age_requirements: Recommended ages or "All ages"
- cost: "Included with admission" or specific pricing
- venue: Always "COSI"
- address: Always "333 W Broad St, Columbus, OH 43215"
- notes: Important details (height requirements, reservations needed, etc.)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Current special exhibits (temporary)
2. Planetarium shows and schedules
3. Live science demonstrations
4. Permanent hands-on exhibits (Space, Ocean, Gadgets, etc.)
5. WOSU PBS Kids area (for younger children)
6. Special events or limited-time experiences

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Planetarium Show: Stars Tonight",
    "date": "Ongoing",
    "time": "Shows at 11am, 1pm, 3pm",
    "description": "Explore the night sky and learn about constellations...",
    "type": "Planetarium Show",
    "age_requirements": "Ages 5+",
    "cost": "Included with admission",
    "venue": "COSI",
    "address": "333 W Broad St, Columbus, OH 43215",
    "notes": "First-come, first-served seating"
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
