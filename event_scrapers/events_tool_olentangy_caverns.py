"""
Olentangy Caverns Events Scraper

Uses AI-assisted web scraping to extract event and operating information from Olentangy Caverns.
Note: This is a seasonal attraction (typically Apr-Oct) with limited event calendar.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_olentangy_caverns_info", description="Get operating hours and special events from Olentangy Caverns. Seasonal attraction with cave tours (54°F year-round temperature).")
def get_olentangy_caverns_info() -> str:
    """
    Scrapes Olentangy Caverns website using AI-assisted extraction.
    Returns operating hours, tour information, and any special events.

    Returns:
        str: JSON with operating info and events, or error message
    """
    url = "https://olentangycaverns.com/"
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
        extraction_prompt = f"""Extract operating information and any special events from this Olentangy Caverns webpage.

Extract:
1. Operating status: Is the cavern currently open or closed? (seasonal operation)
2. Operating hours: Current hours if available
3. Tour information: Any details about cave tours
4. Special events: Any upcoming events or special programs
5. Important notes: Cave temperature, seasonal information, etc.

Return a JSON object with this structure:
{{
  "operating_status": "Open" or "Closed" or "Seasonal - check hours",
  "hours": "Operating hours if available",
  "tour_info": "Tour details",
  "special_events": [
    {{
      "title": "Event name",
      "date": "Event date",
      "description": "Event description"
    }}
  ],
  "notes": "Important visitor information (temperature, seasonal operation, etc.)",
  "venue": "Olentangy Caverns",
  "address": "Olentangy Caverns, Delaware, OH"
}}

If specific information is not available, use empty string or empty array.

Webpage content:
{page_content[:8000]}

Return ONLY valid JSON.
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
            info = json.loads(result)
            return json.dumps(info, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Failed to parse extracted information as JSON: {str(e)}", "raw_response": result})

    except Exception as e:
        return json.dumps({"error": f"Failed to fetch or process information: {str(e)}"})
