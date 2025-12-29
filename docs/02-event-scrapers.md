# Event Scrapers Implementation Plan

## Overview
Expand the family assistant's venue knowledge by adding event scrapers for additional Ohio attractions.

**Implementation Status:** Priority 1, 2 & 3 COMPLETED (19 total scrapers)
**Implementation Approach:** AI-assisted scraping using LangChain WebBaseLoader + LLM extraction

## Current Event Scrapers

### Columbus Area Scrapers (Migrated to AI-Assisted)

#### ✅ 1. Columbus Metro Parks
**File:** `event_scrapers/events_tool_metroparks.py`
**URL:** https://www.metroparks.net/events-new/
**Status:** ✅ COMPLETED (Migrated to AI-assisted)
**Migrated:** 2025-12-22

**What It Scrapes:**
- Nature programs and guided hikes
- Educational workshops
- Family activities and events
- Special events across multiple park locations

**Notes:**
- Multiple outdoor park locations around Columbus
- Most programs are free
- Registration often required
- Weather-dependent activities

---

#### ✅ 2. Columbus Zoo and Aquarium
**File:** `event_scrapers/events_tool_zoo.py`
**URL:** https://columbuszoo.org/events
**Status:** ✅ COMPLETED (Migrated to AI-assisted)
**Migrated:** 2025-12-22

**What It Scrapes:**
- Seasonal events (Wildlights, Boo at the Zoo)
- Animal encounters and experiences
- Educational programs
- Special exhibits

**Notes:**
- Mostly outdoor zoo with some indoor exhibits
- Seasonal events are major attractions
- Member benefits often available
- Weather-dependent for outdoor portions

---

#### ✅ 3. Lynd Fruit Farm
**File:** `event_scrapers/events_tool_lynd_fruit_farm.py`
**URL:** https://lyndfruitfarm.com/events-and-activities
**Status:** ✅ COMPLETED (Migrated to AI-assisted)
**Migrated:** 2025-12-22

**What It Scrapes:**
- Seasonal activities (apple picking, pumpkin patch)
- Special events and festivals
- Farm experiences (hayrides, corn maze)
- Educational programs

**Notes:**
- Outdoor farm location
- Highly seasonal (best in fall)
- Weather-dependent
- Pay-by-activity or pay-by-pound pricing

---

#### ✅ 4. Franklin Park Conservatory
**File:** `event_scrapers/events_tool_conservatory.py`
**URL:** https://www.fpconservatory.org/events/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**What It Scrapes:**
- Exhibitions and special events
- Family programs and workshops
- Seasonal displays
- Age groups and pricing

**Notes:**
- Indoor conservatory + outdoor gardens (not fully indoor)
- Year-round availability
- Educational focus
- Good rain backup option

---

#### ✅ 5. Olentangy Caverns
**File:** `event_scrapers/events_tool_olentangy_caverns.py`
**URL:** https://olentangycaverns.com/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**What It Scrapes:**
- Operating hours and status (seasonal)
- Special events
- Tour information
- Cave conditions

**Notes:**
- Seasonal operation (typically Apr-Oct)
- Cave temperature ~54°F year-round
- Returns operating status + events/tours

---

#### ✅ 6. The Wilds
**File:** `event_scrapers/events_tool_wilds.py`
**URL:** https://thewilds.org/events/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**What It Scrapes:**
- Safari tours and programs
- Special events
- Seasonal offerings
- Zipline and adventure activities

**Notes:**
- 1.5 hour drive from Columbus
- Best for full-day trips
- Seasonal operation

---

### AI-Assisted Scrapers - Priority 2 (Regional: 1-2 hour drive)

#### ✅ 7. Cincinnati Zoo
**File:** `event_scrapers/events_tool_cincinnati_zoo.py`
**URL:** https://cincinnatizoo.org/events/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**Distance:** ~1h 45min from Columbus

**What It Scrapes:**
- Daily events and shows
- Special exhibits
- Festival of Lights (seasonal)
- Educational programs

---

#### ✅ 8. Newport Aquarium
**File:** `event_scrapers/events_tool_newport_aquarium.py`
**URL:** https://www.newportaquarium.com/events
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**Distance:** ~2 hours from Columbus (near Cincinnati)

**What It Scrapes:**
- Animal encounters and interactions
- Special exhibits
- Shows and presentations
- Pricing information

**Notes:**
- Indoor venue - weather-proof
- Family-friendly animal encounters

---

#### ✅ 9. National Museum of the US Air Force
**File:** `event_scrapers/events_tool_airforce_museum.py`
**URL:** https://www.nationalmuseum.af.mil/Visit/Events/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**Distance:** ~1 hour from Columbus (Dayton)

**What It Scrapes:**
- Special events and programs
- IMAX theater schedule
- Temporary exhibits
- Holiday events

**Notes:**
- FREE admission (huge value!)
- Indoor venue - weather-proof
- Educational content
- IMAX tickets separate from admission

---

#### ✅ 10. Kings Island
**File:** `event_scrapers/events_tool_kings_island.py`
**URL:** https://www.visitkingsisland.com/events
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**Distance:** ~1h 45min from Columbus

**What It Scrapes:**
- Operating calendar (seasonal)
- Special events (Halloween Haunt, WinterFest)
- Special shows and entertainment
- New rides/attractions

**Notes:**
- Seasonal operation
- Weather-dependent
- Full-day commitment
- Age/height requirements noted in scraper output

---

#### ✅ 11. Hocking Hills State Park
**File:** `event_scrapers/events_tool_hocking_hills.py`
**URL:** https://www.hockinghills.com/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-22

**Distance:** ~1 hour from Columbus

**What It Provides:**
- Trail information and difficulty
- Seasonal highlights (waterfalls, fall colors, winter ice)
- Outdoor activities (zip-lining nearby)
- Family-friendly trail recommendations

**Notes:**
- Outdoor destination
- Highly weather-dependent
- NOT traditional "events" - provides trail/activity info instead
- Implemented as activities/conditions tool

---

### AI-Assisted Scrapers - Priority 3 (New Venues & Festivals)

#### ✅ 12. COSI (Center of Science and Industry)
**File:** `event_scrapers/events_tool_cosi.py`
**URL:** https://cosi.org/experiences
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**What It Scrapes:**
- Current exhibits (temporary and permanent)
- Planetarium shows and schedules
- Live science demonstrations
- WOSU PBS Kids area

**Notes:**
- Indoor venue - weather-proof
- Great for science-loving kids
- Planetarium shows have limited seating

---

#### ✅ 13. Cedar Point
**File:** `event_scrapers/events_tool_cedar_point.py`
**URL:** https://www.cedarpoint.com/events
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Distance:** ~2+ hours from Columbus (Sandusky, OH)

**What It Scrapes:**
- Operating calendar (seasonal)
- Special events (HalloWeekends, WinterFest)
- New rides and attractions
- Concert series

**Notes:**
- Seasonal operation (May-Oct typically)
- Full-day commitment
- HalloWeekends not ideal for young children

---

#### ✅ 14. Ohio Renaissance Festival
**File:** `event_scrapers/events_tool_ohio_ren_fest.py`
**URL:** https://www.renfestival.com/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Distance:** ~1 hour from Columbus (Waynesville, OH)

**What It Scrapes:**
- Festival dates (late Aug - Oct, weekends only)
- Themed weekends (Pirate Weekend, Celtic Weekend, etc.)
- Entertainment schedule
- Ticket pricing

**Notes:**
- Seasonal: weekends only, late August through October
- Rain or shine event
- Very family-friendly, costume encouraged!

---

#### ✅ 15. Ohio State Fair
**File:** `event_scrapers/events_tool_ohio_state_fair.py`
**URL:** https://ohiostatefair.com/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Location:** Ohio Expo Center, Columbus

**What It Scrapes:**
- Fair dates (late July/August, ~12 days)
- Concert lineup
- Special events and competitions
- Family attractions

**Notes:**
- Annual event, late July/August
- Very family-friendly
- Rides cost extra beyond admission

---

#### ✅ 16. Circleville Pumpkin Show
**File:** `event_scrapers/events_tool_pumpkin_show.py`
**URL:** https://www.pumpkinshow.com/
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Distance:** ~30 min south of Columbus

**What It Scrapes:**
- Festival dates (mid-October, Wed-Sat)
- Parade schedule
- Giant pumpkin displays
- Entertainment and food

**Notes:**
- FREE admission!
- One of world's largest pumpkin festivals
- Very crowded on weekends

---

#### ✅ 17. Ohio State University / Schottenstein Center
**File:** `event_scrapers/events_tool_osu_events.py`
**URL:** https://www.schottensteincenter.com/events
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Location:** OSU Campus, Columbus

**What It Scrapes:**
- Disney on Ice and family shows
- OSU Basketball and Hockey
- Concerts and performances
- Family-friendly events

**Notes:**
- Indoor venue
- Parking available in campus lots
- Great gameday atmosphere even without tickets

---

#### ✅ 18. Nationwide Arena
**File:** `event_scrapers/events_tool_nationwide_arena.py`
**URL:** https://www.nationwidearena.com/events
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Location:** Arena District, Downtown Columbus

**What It Scrapes:**
- Columbus Blue Jackets hockey
- Concerts and shows
- Disney on Ice, WWE, family shows
- Comedy and special events

**Notes:**
- Indoor venue
- Arena District has great dining options
- Family sections available for hockey

---

#### ✅ 19. Columbus Clippers
**File:** `event_scrapers/events_tool_clippers.py`
**URL:** https://www.milb.com/columbus/schedule
**Status:** ✅ COMPLETED (AI-assisted)
**Implemented:** 2025-12-28

**Location:** Huntington Park, Downtown Columbus

**What It Scrapes:**
- Game schedule (April-September)
- Themed nights and promotions
- Fireworks nights
- Giveaways and special events

**Notes:**
- AAA baseball - affordable family entertainment
- Fireworks after many Friday/Saturday games
- Kids can run the bases on Sundays

---

### Future Scrapers (Research)

**Potential additions:**
- Rock and Roll Hall of Fame (Cleveland - 2+ hours)
- Pro Football Hall of Fame (Canton)
- Blendon Woods / Highbanks Metro Parks
- Columbus Crew (MLS soccer)
- Minor league hockey / other sports

---

## Implementation Pattern

### ✅ ACTUAL Implementation (AI-Assisted)

**All Priority 1 & 2 scrapers now use this modern approach:**

```python
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain.chat_models import init_chat_model
import json

@tool("get_venue_events", description="Venue description, distance, key features")
def get_venue_events() -> str:
    """
    Scrapes events using AI-assisted extraction.
    Returns JSON with event details.
    """
    url = "..."
    print(f"Fetching events from {url}...")

    try:
        # Load webpage
        loader = WebBaseLoader(url)
        docs = loader.load()
        page_content = docs[0].page_content

        # Initialize LLM for extraction
        llm = init_chat_model(model="gpt-4o-mini", temperature=0)

        # Prompt LLM to extract structured data
        extraction_prompt = f"""Extract events from this webpage.

        For each event extract:
        - title, date, time, description, type, cost, venue, address, notes

        Return ONLY valid JSON array.

        Webpage: {page_content[:8000]}
        """

        response = llm.invoke(extraction_prompt)
        result = response.content.strip()

        # Clean up markdown code blocks
        if result.startswith('```json'):
            result = result[7:-3]

        return json.dumps(json.loads(result), indent=2)

    except Exception as e:
        return json.dumps({"error": str(e)})
```

**Benefits of AI-Assisted Approach:**
- ⚡ 10x faster to implement
- 🛡️ More resilient to website changes
- 🎯 Works on sites without clear HTML structure
- 🔄 Consistent error handling
- 💰 Cost: ~$0.01 per scraper execution

### Legacy Scraper Structure (BeautifulSoup)

**Used by original 3 scrapers - consider refactoring to AI-assisted:**

```python
from bs4 import BeautifulSoup
import requests
import json
from langchain_core.tools import tool

@tool("get_venue_events", description="...")
def get_venue_events() -> str:
    """Scrapes events using BeautifulSoup HTML parsing"""
    url = "..."
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    # Complex HTML parsing logic...
    events = []
    # ...

    return json.dumps(events, indent=2)
```

### Event Object Schema
```python
{
    "title": "Event Name",
    "date": "2025-12-25",
    "time": "10:00 AM - 5:00 PM",
    "description": "Brief description",
    "venue": "Venue Name",
    "address": "Full address",
    "url": "Event URL",
    "suitable_for_ages": "3-7", # if available
    "indoor_outdoor": "indoor", # if available
    "cost": "Free" or "$X" # if available
}
```

---

## Integration Checklist

For each new scraper:
1. ✅ Create `events_tool_[venue].py` file
2. ✅ Implement scraping logic
3. ✅ Test scraper independently
4. ✅ Import tool in `family_manager.py`
5. ✅ Add to tools list in agent
6. ✅ Update system prompt to mention venue
7. ✅ Test end-to-end with agent
8. ✅ Document any special considerations

---

## Weather-Dependent Recommendations

### Indoor Venues (Rain/Cold Safe)
- Franklin Park Conservatory
- COSI
- Newport Aquarium
- Air Force Museum
- Indoor sections of zoos

### Outdoor Venues (Weather Critical)
- Hocking Hills
- Metro Parks
- The Wilds
- Kings Island
- Olentangy Caverns (partly indoor)

**AI Instruction Update:**
System prompt should include: "For outdoor venues, check the weather forecast and only recommend if conditions are suitable (no heavy rain, reasonable temperature)."

---

## Error Handling Considerations

1. **Website Changes:** Scrapers break when sites redesign
   - Add try/catch blocks
   - Return graceful error messages
   - Log failures for manual review

2. **Seasonal Closures:** Some venues closed in winter
   - Check operating calendar
   - Return closure status clearly

3. **No Events:** Some days have no special events
   - Return basic venue info (hours, admission)
   - Let AI know venue is open even without events

---

## Test-Driven Development Approach

### Philosophy
All event scrapers MUST be developed using Test-Driven Development (TDD):
1. ✅ Write failing test first
2. ✅ Implement scraper to pass test
3. ✅ Refactor while keeping tests green

### Test Suite Structure

```
tests/
├── test_event_scrapers.py
├── fixtures/
│   ├── conservatory_events_sample.html
│   ├── zoo_events_sample.html
│   └── ...
└── conftest.py
```

### Testing Strategy

#### 1. Unit Tests (Required for Each Scraper)

**Test File:** `tests/test_event_scrapers.py`

**Test Cases for Each Scraper:**

```python
import pytest
import json
from unittest.mock import Mock, patch
from events_tool_conservatory import get_conservatory_events

class TestConservatoryEventsScraper:
    """Test suite for Franklin Park Conservatory events scraper."""
    
    @pytest.fixture
    def mock_html_response(self):
        """Load sample HTML from fixtures."""
        with open('tests/fixtures/conservatory_events_sample.html', 'r') as f:
            return f.read()
    
    def test_scraper_returns_valid_json(self, mock_html_response):
        """Test that scraper returns valid JSON string."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=mock_html_response)
            result = get_conservatory_events()
            
            # Should return valid JSON
            events = json.loads(result)
            assert isinstance(events, list)
    
    def test_scraper_extracts_event_fields(self, mock_html_response):
        """Test that all required event fields are extracted."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=mock_html_response)
            result = get_conservatory_events()
            events = json.loads(result)
            
            if len(events) > 0:
                event = events[0]
                # Verify required fields exist
                assert 'title' in event
                assert 'date' in event
                assert 'venue' in event
                assert 'address' in event
                # Optional fields
                assert event.get('description') is not None or event.get('description') == ''
    
    def test_scraper_handles_http_error(self):
        """Test graceful handling of HTTP errors."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=404)
            result = get_conservatory_events()
            
            assert "Failed to fetch events" in result
            assert "404" in result
    
    def test_scraper_handles_no_events(self):
        """Test handling of pages with no events."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text="<html><body></body></html>")
            result = get_conservatory_events()
            
            assert "No events found" in result or result == "[]"
    
    def test_scraper_handles_malformed_html(self):
        """Test handling of malformed HTML without crashing."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text="<html><div>broken</html>")
            result = get_conservatory_events()
            
            # Should not raise exception, should return gracefully
            assert isinstance(result, str)
    
    def test_event_dates_are_valid_format(self, mock_html_response):
        """Test that event dates are in expected format."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=mock_html_response)
            result = get_conservatory_events()
            events = json.loads(result)
            
            for event in events:
                if 'date' in event and event['date']:
                    # Date should be parseable or in recognizable format
                    assert len(event['date']) > 0
                    # Could add more specific format validation
    
    def test_venue_name_is_correct(self, mock_html_response):
        """Test that venue name is correctly set."""
        with patch('requests.get') as mock_get:
            mock_get.return_value = Mock(status_code=200, text=mock_html_response)
            result = get_conservatory_events()
            events = json.loads(result)
            
            for event in events:
                assert event['venue'] == 'Franklin Park Conservatory'
```

**Creating Fixtures:**
1. Visit venue website
2. Save page source to `tests/fixtures/[venue]_events_sample.html`
3. Use in tests to ensure consistent test data
4. Update fixtures periodically when site structure changes

#### 2. Integration Tests

**Test File:** `tests/test_integration.py`

```python
class TestAgentIntegration:
    """Test that scrapers work with the AI agent."""
    
    def test_conservatory_tool_accessible_by_agent(self):
        """Test that agent can call conservatory tool."""
        from family_manager import tools
        tool_names = [tool.name for tool in tools]
        assert 'get_conservatory_events' in tool_names
    
    def test_scraper_output_parseable_by_agent(self):
        """Test that scraper output can be used by AI."""
        result = get_conservatory_events()
        # Should be valid JSON or error message
        try:
            events = json.loads(result)
            assert isinstance(events, list)
        except json.JSONDecodeError:
            # If not JSON, should be error message
            assert isinstance(result, str)
```

#### 3. End-to-End Tests

**Test File:** `tests/test_e2e.py`

```python
@pytest.mark.slow
class TestEndToEnd:
    """End-to-end tests hitting real websites (run sparingly)."""
    
    @pytest.mark.skip(reason="Only run manually to avoid rate limiting")
    def test_conservatory_live_scrape(self):
        """Test actual scraping from live website."""
        result = get_conservatory_events()
        # Should not error on live site
        assert "Failed to fetch" not in result
```

### TDD Workflow for New Scraper

**Step 1: Write the Test FIRST**
```bash
# Create test file
touch tests/test_event_scrapers.py

# Write failing test
cat > tests/test_event_scrapers.py << 'EOF'
def test_conservatory_scraper_exists():
    from events_tool_conservatory import get_conservatory_events
    assert callable(get_conservatory_events)

def test_conservatory_scraper_returns_json():
    from events_tool_conservatory import get_conservatory_events
    result = get_conservatory_events()
    events = json.loads(result)
    assert isinstance(events, list)
EOF
```

**Step 2: Run Test (Should FAIL)**
```bash
pytest tests/test_event_scrapers.py::test_conservatory_scraper_exists -v
# EXPECTED: ImportError or ModuleNotFoundError
```

**Step 3: Implement Minimum Code to Pass**
```python
# events_tool_conservatory.py
def get_conservatory_events() -> str:
    return "[]"  # Minimal implementation
```

**Step 4: Run Test (Should PASS)**
```bash
pytest tests/test_event_scrapers.py::test_conservatory_scraper_returns_json -v
# EXPECTED: PASSED
```

**Step 5: Add More Tests, Implement Features**
Iterate: Add test → Run (fail) → Implement → Run (pass) → Refactor

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-mock

# Run all tests
pytest

# Run specific test file
pytest tests/test_event_scrapers.py

# Run with coverage
pytest --cov=. --cov-report=html

# Run only fast tests (skip slow E2E)
pytest -m "not slow"

# Run in watch mode
pytest-watch
```

### Test Configuration

**File:** `pytest.ini`
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: marks tests as integration tests
    e2e: marks tests as end-to-end tests
addopts = 
    -v
    --tb=short
    --strict-markers
```

### Coverage Requirements

- **Minimum Coverage:** 80% for scraper code
- **Critical Paths:** 100% coverage for error handling
- **Report:** Generate HTML coverage report with each test run

### Continuous Integration

Add to `.github/workflows/test.yml`:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

---

## Future Enhancements

1. **Caching:** Cache events for 24 hours to reduce scraping
2. **Webhooks:** Some venues offer event APIs/RSS feeds
3. **Distance Calculation:** Factor in drive time for recommendations
4. **Traffic Data:** Check real-time traffic for day-of suggestions
