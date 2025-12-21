# Event Scrapers Implementation Plan

## Overview
Expand the family assistant's venue knowledge by adding event scrapers for additional Ohio attractions.

## Current Event Scrapers
- ✅ Columbus Metro Parks (`events_tool_metroparks.py`)
- ✅ Columbus Zoo (`events_tool_zoo.py`)
- ✅ Lynd Fruit Farm (`events_tool_lynd_fruit_farm.py`)

## New Scrapers Needed

### Priority 1: Local Columbus Area

#### 3. Franklin Park Conservatory
**File:** `events_tool_conservatory.py`  
**URL:** https://www.fpconservatory.org/events/  
**Status:** Not Started

**What to Scrape:**
- Exhibitions and special events
- Family programs and workshops
- Seasonal displays
- Hours and admission info

**Notes:**
- Indoor venue (great for bad weather)
- Year-round availability
- Educational focus

---

#### 4. Olentangy Caverns
**File:** `events_tool_olentangy_caverns.py`  
**URL:** https://olentangycaverns.com/  
**Status:** Not Started

**What to Scrape:**
- Operating hours (seasonal)
- Special events
- Tour availability
- Current conditions

**Notes:**
- Seasonal operation (typically Apr-Oct)
- Cave temperature ~54°F year-round
- Limited event calendar

---

#### 5. The Wilds
**File:** `events_tool_wilds.py`  
**URL:** https://thewilds.org/events/  
**Status:** Not Started

**What to Scrape:**
- Safari tours and programs
- Special events
- Seasonal offerings
- Zipline and adventure activities

**Notes:**
- 1.5 hour drive from Columbus
- Best for full-day trips
- Seasonal operation

---

### Priority 2: Regional Attractions (1-2 hour drive)

#### 6. Cincinnati Zoo
**File:** `events_tool_cincinnati_zoo.py`  
**URL:** https://cincinnatizoo.org/events/  
**Status:** Not Started

**Distance:** ~1h 45min from Columbus

**What to Scrape:**
- Daily events and shows
- Special exhibits
- Festival of Lights (seasonal)
- Operating hours

---

#### 7. Newport Aquarium
**File:** `events_tool_newport_aquarium.py`  
**URL:** https://www.newportaquarium.com/events  
**Status:** Not Started

**Distance:** ~2 hours from Columbus (near Cincinnati)

**What to Scrape:**
- Animal encounters
- Special exhibits
- Operating hours
- Combo deals with Cincinnati Zoo

---

#### 8. National Museum of the US Air Force
**File:** `events_tool_airforce_museum.py`  
**URL:** https://www.nationalmuseum.af.mil/Visit/Events/  
**Status:** Not Started

**Distance:** ~1 hour from Columbus (Dayton)

**What to Scrape:**
- Special events and programs
- IMAX theater schedule
- Temporary exhibits
- Hours (FREE admission)

**Notes:**
- Free admission (huge value)
- Indoor venue
- Educational content

---

#### 9. Kings Island
**File:** `events_tool_kings_island.py`  
**URL:** https://www.visitkingsisland.com/events  
**Status:** Not Started

**Distance:** ~1h 45min from Columbus

**What to Scrape:**
- Operating calendar (seasonal)
- Special events (Halloween Haunt, WinterFest)
- Height requirements for rides
- Weather-related closures

**Notes:**
- Seasonal operation
- Weather-dependent
- Full-day commitment

---

#### 10. Hocking Hills State Park
**File:** `events_tool_hocking_hills.py`  
**URL:** Multiple sources  
**Status:** Not Started

**Distance:** ~1 hour from Columbus

**What to Provide:**
- Trail conditions
- Seasonal highlights (waterfalls, fall colors, winter ice)
- Nearby activities (zip-lining, canoeing)
- Weather considerations

**Notes:**
- Outdoor destination
- Highly weather-dependent
- May not have traditional "events"
- Could be more of an activities/conditions tool

---

### Priority 3: Discovery & Research

#### 11. Additional Ohio Attractions
**Status:** Not Started

**Research Needed:**
- COSI (Columbus) - science museum
- Ohio State Fair (seasonal)
- Blendon Woods Metro Park (nature center)
- Highbanks Metro Park
- Cedar Point (Sandusky - 2+ hours)
- Rock and Roll Hall of Fame (Cleveland - 2+ hours)
- Pro Football Hall of Fame (Canton)
- Local festivals and seasonal events

---

## Implementation Pattern

### Standard Scraper Structure
```python
from bs4 import BeautifulSoup
import requests
import json
from langchain_core.tools import tool

@tool("get_venue_events", description="...")
def get_venue_events() -> str:
    """
    Scrapes events from [Venue Name].
    Returns JSON with event details.
    """
    url = "..."
    print(f"Fetching events from {url}...")
    
    response = requests.get(url)
    if response.status_code != 200:
        return f"Failed to fetch events. Status code: {response.status_code}"
    
    soup = BeautifulSoup(response.text, "html.parser")
    events = []
    
    # Parsing logic here
    
    if not events:
        return "No events found."
    
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
