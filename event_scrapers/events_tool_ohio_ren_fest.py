"""
Ohio Renaissance Festival Events Scraper

Uses AI-assisted web scraping to extract event information from Ohio Renaissance Festival.
Note: Seasonal festival (typically late Aug - Oct, weekends only).
Located near Waynesville, about 1 hour from Columbus.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_ohio_ren_fest_events", description="Get schedule and themed weekends from Ohio Renaissance Festival near Waynesville, OH. Seasonal: late Aug - Oct, weekends only. About 1 hour from Columbus. Features jousting, shows, food, crafts, and themed weekends.")
def get_ohio_ren_fest_events() -> str:
    """
    Scrapes Ohio Renaissance Festival website using AI-assisted extraction.
    Returns operating schedule, themed weekends, and special events.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.renfestival.com/"
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
        extraction_prompt = f"""Extract all festival information, themed weekends, and events from this Ohio Renaissance Festival webpage.

For each themed weekend or event, extract:
- title: Weekend theme or event name
- date: Specific dates (weekends only during season)
- time: Festival hours (typically 10:30 AM - 6:00 PM or similar)
- description: What makes this weekend special, theme details
- type: Type (e.g., "Themed Weekend", "Opening Weekend", "Closing Weekend", "Special Event", "Season Info")
- age_requirements: "Family-friendly" or specific age notes
- cost: Ticket prices (adult, child, discount days)
- venue: Always "Ohio Renaissance Festival"
- address: Always "10542 E State Route 73, Waynesville, OH 45068"
- notes: Important details (weather policy, costume encouraged, what's included)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Current season dates (is the festival running?)
2. Themed weekends (Pirate Weekend, Celtic Weekend, etc.)
3. Opening and closing weekends
4. Daily entertainment (jousting, shows, performances)
5. Family-friendly activities
6. Ticket pricing and discount days (often cheaper on Sundays or specific days)

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Pirate Invasion Weekend",
    "date": "September 14-15, 2025",
    "time": "10:30 AM - 6:00 PM",
    "description": "Ahoy! Pirates take over the village with nautical shows, sea shanties, and treasure hunts...",
    "type": "Themed Weekend",
    "age_requirements": "Family-friendly",
    "cost": "Adults $28, Children (5-12) $14, Under 5 Free",
    "venue": "Ohio Renaissance Festival",
    "address": "10542 E State Route 73, Waynesville, OH 45068",
    "notes": "Rain or shine event. Costume encouraged!"
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
