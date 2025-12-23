"""
Franklin Park Conservatory Events Scraper

Uses AI-assisted web scraping to extract event information from Franklin Park Conservatory's website.
This approach is more resilient to minor website changes compared to traditional HTML parsing.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_conservatory_events", description="Get upcoming events from Franklin Park Conservatory in Columbus, OH. Indoor venue great for all weather conditions.")
def get_conservatory_events() -> str:
    """
    Scrapes Franklin Park Conservatory events page using AI-assisted extraction.
    Returns a JSON string with event details.

    Returns:
        str: JSON array of events or error message
    """
    url = "https://www.fpconservatory.org/events/"
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
        extraction_prompt = f"""Extract all upcoming events from this Franklin Park Conservatory events webpage.

For each event, extract:
- title: Event name
- date: Event date (keep original format from page)
- time: Event time if available
- description: Brief description if available
- age_group: Target audience (e.g., "All Ages", "21+ Only")
- cost: Admission cost or pricing details if mentioned
- venue: Always "Franklin Park Conservatory"
- address: Always "1777 E Broad St, Columbus, OH 43203"

Return ONLY a valid JSON array of events. Each event should be a JSON object with the fields above.
If a field is not available, use an empty string.

Only include events that are clearly listed on the page. Do not make up events.

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Event Name",
    "date": "Jan 4",
    "time": "",
    "description": "Event description",
    "age_group": "All Ages",
    "cost": "Free with Columbus or Franklin County ID",
    "venue": "Franklin Park Conservatory",
    "address": "1777 E Broad St, Columbus, OH 43203"
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
