"""
Event Scrapers Package

This package contains web scrapers for various family-friendly venues in the Columbus, OH area.
Each scraper is implemented as a LangChain tool that can be called by the AI agent.

Scraper Types:
- Legacy scrapers: Traditional BeautifulSoup HTML parsing (metroparks, zoo, lynd_fruit_farm)
- AI-assisted scrapers: LLM-based content extraction (conservatory, olentangy_caverns, wilds)
"""

# Legacy scrapers (BeautifulSoup-based)
from event_scrapers.events_tool_metroparks import get_metroparks_events
from event_scrapers.events_tool_zoo import get_zoo_events
from event_scrapers.events_tool_lynd_fruit_farm import get_lynd_fruit_farm_events

# AI-assisted scrapers (LLM-based)
from event_scrapers.events_tool_conservatory import get_conservatory_events
from event_scrapers.events_tool_olentangy_caverns import get_olentangy_caverns_info
from event_scrapers.events_tool_wilds import get_wilds_events

__all__ = [
    # Legacy scrapers
    'get_metroparks_events',
    'get_zoo_events',
    'get_lynd_fruit_farm_events',
    # AI-assisted scrapers
    'get_conservatory_events',
    'get_olentangy_caverns_info',
    'get_wilds_events',
]
