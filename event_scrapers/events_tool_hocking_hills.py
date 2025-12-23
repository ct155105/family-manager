"""
Hocking Hills State Park Information Tool

Uses AI-assisted web scraping to extract trail and activity information.
Note: 1 hour from Columbus - outdoor destination, highly weather-dependent.
Unlike other scrapers, this focuses on trail conditions and outdoor activities rather than scheduled events.
"""

from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json
import os


@tool("get_hocking_hills_info", description="Get trail conditions and activities at Hocking Hills State Park. 1 hour from Columbus, outdoor destination with waterfalls and hiking - very weather-dependent.")
def get_hocking_hills_info() -> str:
    """
    Scrapes Hocking Hills information using AI-assisted extraction.
    Returns trail conditions, seasonal highlights, and available activities.

    Returns:
        str: JSON with trail/activity information or error message
    """
    # Note: Hocking Hills doesn't have a single events page like other venues
    # Using main parks page for general information
    url = "https://www.hockinghills.com/"
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
        extraction_prompt = f"""Extract trail and activity information from this Hocking Hills webpage.

This is NOT a traditional events venue - it's a state park with hiking trails and natural features.

Extract information about:
- title: Trail or activity name
- description: What to do/see (e.g., "Old Man's Cave Trail - 1 mile hike to waterfall")
- type: Type (e.g., "Hiking Trail", "Natural Feature", "Outdoor Activity", "Zip-lining")
- difficulty: Trail difficulty if mentioned (easy, moderate, difficult)
- distance: Trail length if mentioned
- seasonal_notes: Best time to visit, seasonal highlights (fall colors, winter ice formations, spring waterfalls)
- family_friendly: Is it suitable for young children?
- venue: Always "Hocking Hills State Park"
- location: Specific park area if mentioned (Old Man's Cave, Ash Cave, Cedar Falls, etc.)
- notes: Important details (weather-dependent, proper footwear needed, etc.)

Return ONLY a valid JSON array. Each item should be a JSON object with the fields above.
If a field is not available, use an empty string.

Focus on:
1. Popular hiking trails
2. Waterfall viewing areas
3. Family-friendly outdoor activities
4. Seasonal highlights
5. Zip-lining and adventure activities nearby

Webpage content:
{page_content[:8000]}

Return format:
[
  {{
    "title": "Old Man's Cave Trail",
    "description": "1-mile loop trail featuring caves, waterfalls, and rock formations",
    "type": "Hiking Trail",
    "difficulty": "Moderate",
    "distance": "1 mile loop",
    "seasonal_notes": "Spring: high waterfalls, Fall: colorful foliage, Winter: ice formations",
    "family_friendly": "Yes - some steps and uneven terrain",
    "venue": "Hocking Hills State Park",
    "location": "Old Man's Cave area",
    "notes": "Weather-dependent. Proper footwear required. Can be slippery when wet."
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
            info = json.loads(result)
            if not isinstance(info, list):
                return json.dumps({"error": "Extracted data is not a list"})
            return json.dumps(info, indent=2)
        except json.JSONDecodeError as e:
            return json.dumps({"error": f"Failed to parse extracted information as JSON: {str(e)}", "raw_response": result})

    except Exception as e:
        return json.dumps({"error": f"Failed to fetch or process information: {str(e)}"})
