"""
Circleville Pumpkin Show Events Scraper

Uses AI-assisted web scraping to extract event information from Circleville Pumpkin Show.
Note: Annual festival in mid-October (Wed-Sat), about 30 min south of Columbus.
One of the largest and oldest pumpkin festivals in the world!
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_pumpkin_show_events", description="Get schedule and events from Circleville Pumpkin Show, one of the world's largest pumpkin festivals. Annual event in mid-October (Wed-Sat), about 30 min south of Columbus. FREE admission! Features giant pumpkins, parades, food, rides.")
def get_pumpkin_show_events() -> str:
    """
    Scrapes Circleville Pumpkin Show website using AI-assisted extraction.
    Returns festival schedule, parades, and special events.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.pumpkinshow.com/"
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
        extraction_prompt = f"""Extract all festival information and events from this Circleville Pumpkin Show webpage.

For each event or attraction, extract:
- title: Event or attraction name
- date: Specific dates (typically Wed-Sat in mid-October)
- time: Event time if applicable
- description: What visitors can experience
- type: Type (e.g., "Parade", "Competition", "Entertainment", "Food Event", "Festival Info")
- age_requirements: Any age notes or "All ages - very family friendly"
- cost: "FREE admission" for the festival itself, or specific costs for rides
- venue: Always "Circleville Pumpkin Show"
- address: Always "Downtown Circleville, OH (about 30 min south of Columbus)"
- notes: Important details (parking, best times to visit, weather)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Festival dates and hours
2. Parade schedule (Baby Parade, Pet Parade, main parades)
3. Giant pumpkin weigh-off and displays
4. Entertainment and performances
5. Pumpkin food specialties (pumpkin donuts, pumpkin pie, etc.)
6. Rides and carnival attractions
7. Miss Pumpkin Show pageant

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "2025 Circleville Pumpkin Show",
    "date": "October 15-18, 2025",
    "time": "Wed-Fri 11AM-11PM, Sat 9AM-11PM",
    "description": "One of the world's largest pumpkin festivals featuring giant pumpkins, 7 parades, carnival rides, and famous pumpkin foods...",
    "type": "Festival Info",
    "age_requirements": "All ages - very family friendly",
    "cost": "FREE admission (rides cost extra)",
    "venue": "Circleville Pumpkin Show",
    "address": "Downtown Circleville, OH (about 30 min south of Columbus)",
    "notes": "Very crowded on weekends. Wednesday/Thursday less busy. Street parking available but fills quickly."
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
