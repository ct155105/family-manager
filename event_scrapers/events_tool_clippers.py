"""
Columbus Clippers Events Scraper

Uses AI-assisted web scraping to extract event information from Columbus Clippers.
AAA affiliate of Cleveland Guardians. Plays at Huntington Park downtown.
Great family-friendly baseball experience with promotions and themed nights.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json


@tool("get_clippers_events", description="Get game schedule and promotions from Columbus Clippers (AAA baseball) at Huntington Park. Family-friendly with fireworks nights, themed games, and affordable tickets. Season: April-September.")
def get_clippers_events() -> str:
    """
    Scrapes Columbus Clippers schedule using AI-assisted extraction.
    Returns upcoming games, promotions, and special events.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.milb.com/columbus/schedule"
    print(f"Fetching schedule from {url}...")

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
        extraction_prompt = f"""Extract upcoming Columbus Clippers baseball games and promotions from this webpage.

For each game or event, extract:
- title: Game matchup or event name (e.g., "Clippers vs Toledo Mud Hens")
- date: Game date
- time: Game time (usually 6:35 PM or 7:05 PM weeknights, earlier on weekends)
- description: Any special theme or promotion for that game
- type: Type (e.g., "Home Game", "Fireworks Night", "Themed Night", "Giveaway", "Special Event")
- age_requirements: "All ages - family friendly"
- cost: Ticket prices if mentioned (usually $10-30 range)
- venue: Always "Huntington Park"
- address: Always "330 Huntington Park Ln, Columbus, OH 43215"
- notes: Special promotions (fireworks, bobblehead giveaway, dollar dog night, etc.)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Upcoming home games (next 2 weeks if possible)
2. Fireworks nights (usually Fridays/Saturdays)
3. Themed nights (Star Wars night, Princess night, etc.)
4. Giveaway promotions (bobbleheads, t-shirts)
5. Dollar dog nights or food specials
6. Kids activities (run the bases, etc.)

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Clippers vs Toledo Mud Hens",
    "date": "July 4, 2025",
    "time": "7:05 PM",
    "description": "Independence Day celebration with postgame fireworks spectacular!",
    "type": "Fireworks Night",
    "age_requirements": "All ages - family friendly",
    "cost": "$12 - $28",
    "venue": "Huntington Park",
    "address": "330 Huntington Park Ln, Columbus, OH 43215",
    "notes": "Fireworks after the game! Arrive early for best parking. Kids can run the bases after Sunday games."
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
