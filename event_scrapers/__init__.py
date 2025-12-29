"""
Event Scrapers Package

This package contains web scrapers for various family-friendly venues in the Columbus, OH area.
Each scraper is implemented as a LangChain tool that can be called by the AI agent.

Scraper Types:
- Legacy scrapers: Traditional BeautifulSoup HTML parsing (metroparks, zoo, lynd_fruit_farm)
- AI-assisted scrapers: LLM-based content extraction (all others)

Total: 19 scrapers covering museums, zoos, parks, amusement parks, sports, and seasonal festivals.
"""

# Legacy scrapers (BeautifulSoup-based)
from event_scrapers.events_tool_metroparks import get_metroparks_events
from event_scrapers.events_tool_zoo import get_zoo_events
from event_scrapers.events_tool_lynd_fruit_farm import get_lynd_fruit_farm_events

# AI-assisted scrapers - Priority 1 (Columbus area)
from event_scrapers.events_tool_conservatory import get_conservatory_events
from event_scrapers.events_tool_olentangy_caverns import get_olentangy_caverns_info
from event_scrapers.events_tool_wilds import get_wilds_events

# AI-assisted scrapers - Priority 2 (Regional: 1-2 hour drive)
from event_scrapers.events_tool_cincinnati_zoo import get_cincinnati_zoo_events
from event_scrapers.events_tool_newport_aquarium import get_newport_aquarium_events
from event_scrapers.events_tool_airforce_museum import get_airforce_museum_events
from event_scrapers.events_tool_kings_island import get_kings_island_events
from event_scrapers.events_tool_hocking_hills import get_hocking_hills_info

# AI-assisted scrapers - Priority 3 (New venues & festivals)
from event_scrapers.events_tool_cosi import get_cosi_events
from event_scrapers.events_tool_cedar_point import get_cedar_point_events
from event_scrapers.events_tool_ohio_ren_fest import get_ohio_ren_fest_events
from event_scrapers.events_tool_ohio_state_fair import get_ohio_state_fair_events
from event_scrapers.events_tool_pumpkin_show import get_pumpkin_show_events
from event_scrapers.events_tool_osu_events import get_osu_events
from event_scrapers.events_tool_nationwide_arena import get_nationwide_arena_events
from event_scrapers.events_tool_clippers import get_clippers_events

__all__ = [
    # Legacy scrapers
    'get_metroparks_events',
    'get_zoo_events',
    'get_lynd_fruit_farm_events',
    # AI-assisted scrapers - Priority 1
    'get_conservatory_events',
    'get_olentangy_caverns_info',
    'get_wilds_events',
    # AI-assisted scrapers - Priority 2
    'get_cincinnati_zoo_events',
    'get_newport_aquarium_events',
    'get_airforce_museum_events',
    'get_kings_island_events',
    'get_hocking_hills_info',
    # AI-assisted scrapers - Priority 3 (New)
    'get_cosi_events',
    'get_cedar_point_events',
    'get_ohio_ren_fest_events',
    'get_ohio_state_fair_events',
    'get_pumpkin_show_events',
    'get_osu_events',
    'get_nationwide_arena_events',
    'get_clippers_events',
]
