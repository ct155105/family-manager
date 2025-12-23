# GitHub Copilot Instructions for Family Manager

## Developer Context

**Developer:** Engineering Director learning agentic AI systems through hands-on implementation

**Coaching Approach - IMPORTANT:**
- **Explain the "why" behind decisions**, not just the "how"
- **Present architectural trade-offs** and decision frameworks
- **Ask guiding questions** to help developer think through problems
- **Use analogies and mental models** to explain complex concepts
- **Reference industry patterns** (YAGNI, SOLID, etc.) when relevant
- **Encourage critical thinking** - challenge assumptions, explore alternatives
- **Provide context** for tool vs. function decisions, agent architecture, etc.
- **Document decisions** inline with reasoning for future reference

**Learning Goals:**
- Understanding agentic system architecture (tools vs. context, state management)
- Best practices for LangChain/LangGraph implementation
- Cost/performance optimization for LLM-based systems
- Professional software engineering practices (TDD, git workflow, code review)
- Balancing simplicity (YAGNI) with extensibility

**Examples of Good Coaching:**
- ✅ "Should we make this a tool? Let's think through when tools make sense..."
- ✅ "This could be solved 3 ways. Here are the trade-offs..."
- ✅ "Notice how this pattern reduces LLM calls? Here's why that matters..."
- ❌ "Do this" (without explanation)
- ❌ Implementing without discussing alternatives

---

## Project Context

This is a family weekend planning assistant that uses AI (LangChain/LangGraph) to generate personalized activity recommendations based on:
- Weather forecasts
- Local events from various venues
- Children's ages and interests
- Recommendation history (to avoid repeats)

The system scrapes event information from Ohio attractions and sends daily email recommendations via Gmail API.

---

## Development Principles

### 1. Test-Driven Development (TDD) - MANDATORY

**All new code MUST follow TDD:**

1. ✅ **Write the test FIRST** - Before writing any implementation code
2. ✅ **Run the test and watch it FAIL** - Verify test catches the missing functionality
3. ✅ **Write minimal code to pass** - Implement only what's needed for the test
4. ✅ **Run test again and watch it PASS** - Verify implementation works
5. ✅ **Refactor** - Clean up code while keeping tests green
6. ✅ **Repeat** - Add next test, implement, refactor

**Example TDD Workflow:**
```python
# Step 1: Write failing test
def test_new_scraper_extracts_title():
    result = get_new_venue_events()
    events = json.loads(result)
    assert events[0]['title'] == 'Expected Title'

# Step 2: Run pytest (FAILS - function doesn't exist)

# Step 3: Implement
def get_new_venue_events():
    return '[{"title": "Expected Title"}]'

# Step 4: Run pytest (PASSES)

# Step 5: Refactor and add more tests
```

**When implementing event scrapers:**
- Start with `test_event_scrapers.py` 
- Write test for basic functionality
- Create scraper file only after test exists
- Implement scraper to pass test
- Add more tests for edge cases
- Refactor scraper while keeping tests green

---

### 2. Code Quality Standards

**Type Hints:**
- Use type hints for all function parameters and return values
- Example: `def get_events(location: str = 'Columbus,OH,US') -> str:`

**Documentation:**
- Every function needs a docstring explaining purpose, args, and return value
- Complex logic needs inline comments
- **CRITICAL: Update `/docs` files in the SAME commit as implementation**
  - When adding scrapers → Update `docs/02-event-scrapers.md` status from ⏳ PLANNED to ✅ COMPLETED
  - When changing features → Update relevant doc files to reflect new behavior
  - Documentation updates are NOT optional - they're part of the Definition of Done

**Error Handling:**
- Always handle HTTP errors gracefully
- Return user-friendly error messages, not stack traces
- Log errors for debugging but don't expose to end users

**Logging:**
- Use `print()` for important status updates (goes to Cloud Logging in production)
- Format: `print(f"Fetching events from {url}...")`
- Include context in error messages

---

### 3. Web Scraping Best Practices

**Two Implementation Approaches:**

**1. AI-Assisted Scraping (PREFERRED for new scrapers):**
- Use LangChain WebBaseLoader + gpt-4o-mini for content extraction
- 10x faster to implement than traditional BeautifulSoup parsing
- More resilient to minor HTML structure changes
- Pattern:
  ```python
  from langchain_community.document_loaders import WebBaseLoader
  from langchain.chat_models import init_chat_model

  loader = WebBaseLoader(url)
  docs = loader.load()

  llm = init_chat_model(model="gpt-4o-mini", model_provider="openai", temperature=0)
  response = llm.invoke(extraction_prompt)
  ```
- See `event_scrapers/events_tool_conservatory.py` for reference implementation

**2. Traditional BeautifulSoup (DEPRECATED):**
- All legacy scrapers have been migrated to AI-assisted approach
- Do NOT use BeautifulSoup for new scrapers
- If you encounter a BeautifulSoup scraper, consider migrating it

**For All Event Scrapers (`event_scrapers/events_tool_*.py`):**
- Always check HTTP status code before parsing
- Return JSON string with consistent schema:
  ```json
  [
    {
      "title": "Event Name",
      "date": "YYYY-MM-DD or descriptive string",
      "time": "HH:MM AM - HH:MM PM",
      "description": "Brief description",
      "venue": "Venue Name",
      "address": "Full address",
      "url": "Event URL (optional)"
    }
  ]
  ```
- Return `"No events found."` if page has no events
- Handle malformed HTML without crashing

**Website Changes:**
- Scrapers WILL break when websites redesign
- Write defensive code with try/except blocks
- Fail gracefully with informative messages

---

### 4. LangChain/LangGraph Patterns

**Tools:**
- Decorate with `@tool()` from `langchain_core.tools`
- Provide clear, descriptive tool descriptions for the AI
- Return strings (JSON or plain text), not complex objects
- Example:
  ```python
  @tool("get_weather_forecast", description="Get detailed weather forecast for Columbus, OH for the next 3 days.")
  def get_weekend_forecast(location: str = 'Columbus,OH,US') -> str:
  ```

**System Prompts:**
- Be explicit about what the AI should do
- Include constraints (e.g., "no more than 3 recommendations")
- Mention available tools
- Update in `family_manager.py` when adding new capabilities

**Agent Configuration:**
- Current model: `gpt-5.2` (configurable in `family_manager.py`)
- Max iterations: 15 (allows agent to check all 11 scrapers if needed)
- Use ReAct pattern for tool-using agents
- Each iteration = one reasoning cycle + one tool call

**Architectural Pattern: Static Context vs. Dynamic Actions**

This project follows a clear pattern for deciding what should be pre-fetched vs. provided as tools:

**Static Context (Pre-fetched in `create_messages()`):**
- Information needed for 100% of executions
- Doesn't change during conversation
- Cheaper/faster to include upfront
- Examples: weather forecast, today's date, children's ages

**Dynamic Actions (Provided as Tools):**
- Information that may or may not be needed
- Agent decides when to fetch based on context
- Can be called multiple times with different parameters
- Examples: event scrapers (Metro Parks, Zoo, Lynd Fruit Farm)

**Decision Framework:**
Ask these questions when adding new functionality:
1. "Will I use this in >80% of requests?" → Pre-fetch
2. "Does the agent need to decide IF/WHEN to use this?" → Tool
3. "Could the agent make a mistake by forgetting to check?" → Pre-fetch
4. "Does this have side effects or high cost?" → Tool
5. "Is this conditional on user request?" → Tool

**Benefits of this pattern:**
- Reduces LLM calls (fewer reasoning loops)
- Lower token costs (less tool-calling overhead)
- More reliable (agent can't forget critical context)
- Clearer separation of concerns

See commit `3b34c8d` for example refactoring weather from tool to pre-fetch.

---

### 5. Configuration Management

**Secrets:**
- Never commit API keys or credentials
- Use `.env` file for local development
- Use Secret Manager in GCP production
- Pattern in `config/gcp_config.py`

**Family Data:**
- Store children birthdates in config (not ages directly)
- Calculate ages dynamically at runtime
- Keep interests separate and updateable
- See `/docs/01-personalization-and-state.md`

---

### 6. File Organization

**Project Structure:**
```
family-manager/
├── family_manager.py          # Main agent workflow
├── weather_forecaster.py      # Weather tool
├── email_client.py           # Gmail integration
├── event_scrapers/           # Event scrapers package
│   ├── __init__.py          # Exports all scrapers
│   ├── events_tool_*.py     # Individual venue scrapers
│   └── scraper_template.py  # Template for new scrapers
├── config/                   # Configuration files
├── database/                 # Firestore clients (future)
├── tests/                    # Test files
│   ├── test_event_scrapers.py
│   ├── test_integration.py
│   └── fixtures/             # Sample HTML for tests
├── docs/                     # Documentation
└── .github/                  # CI/CD and instructions
```

**Naming Conventions:**
- Event scrapers: `event_scrapers/events_tool_[venue_name].py`
- Tool functions: `get_[venue]_events()` or `get_[venue]_info()`
- Test files: `test_[module_name].py`
- Test functions: `test_[specific_functionality]()`

---

### 7. Git and Version Control

**Commit Messages:**
- Use conventional commits format
- Examples:
  - `feat: add Franklin Park Conservatory event scraper`
  - `test: add TDD tests for conservatory scraper`
  - `fix: correct weather location from GA to OH`
  - `docs: update deployment architecture`
  - `refactor: simplify event JSON structure`

**Branch Strategy:**
- Main branch: `main` (protected)
- Feature branches: `feature/scraper-conservatory`
- Test branches: `test/tdd-scrapers`

**Before Committing:**
- Run tests: `pytest`
- Check coverage: `pytest --cov=.`
- Verify no secrets in code
- **REQUIRED: Update docs in `/docs` to reflect implementation changes**
  - Mark tasks as ✅ COMPLETED in task tracking docs
  - Update code examples to match implementation
  - Add implementation notes and dates

---

### 8. Testing Requirements

**Required Tests for Event Scrapers:**
1. ✅ Returns valid JSON
2. ✅ Extracts all required fields
3. ✅ Handles HTTP errors gracefully
4. ✅ Handles pages with no events
5. ✅ Handles malformed HTML
6. ✅ Sets correct venue name
7. ✅ Validates date formats

**Coverage Goals:**
- Overall: 80% minimum
- Scrapers: 90% minimum
- Error paths: 100%

**Test Commands:**
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test
pytest tests/test_event_scrapers.py::TestConservatoryEventsScraper::test_scraper_returns_valid_json

# Run only fast tests
pytest -m "not slow"
```

---

### 9. AI Agent Behavior

**Weather Considerations:**
- ALWAYS check weather FIRST
- Only recommend outdoor activities if weather is suitable
- Provide indoor alternatives in bad weather
- Current weather tool uses Columbus, OH (not GA - location bug fixed)

**Recommendation Logic:**
- Provide EXACTLY 3 recommendations
- Rank them 1, 2, 3 with reasoning
- Consider children's ages: currently dynamic (will be calculated from birthdates)
- Check recommendation history to avoid repeats (future feature)
- Align with children's interests when possible

**Newsletter Generation:**
- Create HTML email from recommendations
- Include weather summary
- Format for easy reading by parents
- Send via Gmail API

---

### 10. Performance and Costs

**Scraping:**
- Cache results when possible (future)
- Don't scrape same site multiple times in one run
- Respect robots.txt
- Add small delays if hitting rate limits

**AI Costs:**
- GPT-5.2 is expensive - be judicious with calls
- Limit max iterations to 5
- Consider GPT-5-mini for simpler tasks
- Track token usage in production

**Cloud Costs:**
- Cloud Run scales to zero (minimal cost)
- Firestore: optimize queries
- Secret Manager: cache secrets, don't fetch repeatedly

---

### 11. Deployment Awareness

**Environment Detection:**
```python
import os
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"
```

**Local Development:**
- Use `.env` file for secrets
- Use `python family_manager.py` to run
- Gmail creates drafts (not auto-sends)

**GCP Production:**
- Secrets from Secret Manager
- Scheduled via Cloud Scheduler
- Logs to Cloud Logging
- State in Firestore

---

### 12. Documentation - CRITICAL REQUIREMENT

**Documentation is NOT optional - it's part of the Definition of Done**

**Update in SAME commit as implementation:**
- Adding new venues → Update `docs/02-event-scrapers.md` (mark ✅ COMPLETED, add date, update "What It Scrapes")
- Changing AI behavior → Update `docs/03-model-evals.md` or create new doc
- Modifying deployment → Update `docs/04-deployment-architecture.md`
- Adding family features → Update `docs/01-personalization-and-state.md`

**Documentation Checklist:**
- ✅ Task status updated from ⏳ PLANNED to ✅ COMPLETED
- ✅ Implementation date added (e.g., "Implemented: 2025-12-22")
- ✅ Code examples match actual implementation
- ✅ Implementation notes added (e.g., "Uses AI-assisted scraping, not BeautifulSoup")
- ✅ Architecture diagrams reflect current reality

**Keep Current:**
- Code examples in docs should match actual implementation
- Architecture diagrams reflect reality
- Task statuses updated when completed
- **NEVER commit code without updating corresponding documentation**

---

## Common Tasks

### Adding a New Event Scraper

1. **Write tests first** in `tests/test_event_scrapers.py`:
   ```python
   class TestNewVenueScraper:
       def test_scraper_returns_valid_json(self):
           # Test implementation
   ```

2. **Run test and verify it fails:**
   ```bash
   pytest tests/test_event_scrapers.py::TestNewVenueScraper -v
   ```

3. **Create scraper file** `event_scrapers/events_tool_new_venue.py`:
   ```python
   from langchain_community.document_loaders import WebBaseLoader
   from langchain_core.tools import tool
   from langchain.chat_models import init_chat_model

   @tool("get_new_venue_events", description="...")
   def get_new_venue_events() -> str:
       # AI-assisted implementation
   ```

4. **Run test until it passes:**
   ```bash
   pytest tests/test_event_scrapers.py::TestNewVenueScraper -v
   ```

5. **Update package exports** in `event_scrapers/__init__.py`:
   ```python
   from event_scrapers.events_tool_new_venue import get_new_venue_events
   __all__ = [..., 'get_new_venue_events']
   ```

6. **Import in `family_manager.py`:**
   ```python
   from event_scrapers import get_new_venue_events
   tools = [..., get_new_venue_events]
   ```

7. **Update system prompt** to mention new venue

8. **Test end-to-end:**
   ```bash
   python family_manager.py
   ```

9. **REQUIRED: Update documentation** in `docs/02-event-scrapers.md`:
   - Change status from ⏳ PLANNED to ✅ COMPLETED
   - Add implementation date
   - Update "What to Scrape" to "What It Scrapes"
   - Add any implementation notes

---

### Debugging Issues

**Scraper Not Working:**
1. Check website hasn't changed structure
2. Verify HTTP status code
3. Print `soup` HTML to inspect
4. Test with fixture HTML first
5. Check for JavaScript-rendered content (may need Selenium)

**AI Not Using Tool:**
1. Verify tool description is clear
2. Check tool is in tools list
3. Review system prompt mentions the venue
4. Check max_iterations isn't too low
5. Review agent logs for tool calls

**Weather Wrong:**
- Verify location string: `'Columbus,OH,US'` (not `'Columbus,US,OH'`)
- Check API key is valid
- Test weather tool independently

---

## Code Review Checklist

Before submitting code, verify:
- ✅ Tests written BEFORE implementation (TDD)
- ✅ All tests pass
- ✅ Coverage > 80%
- ✅ Type hints on all functions
- ✅ Docstrings on public functions
- ✅ No secrets committed
- ✅ Error handling in place
- ✅ Logging for debugging
- ✅ **CRITICAL: Documentation updated in `/docs` (SAME commit as code)**
  - Task status changed from ⏳ PLANNED to ✅ COMPLETED
  - Implementation date added
  - Code examples updated to match implementation
  - Implementation notes added
- ✅ Conventional commit message

---

## Learning Resources

- **LangChain Docs:** https://python.langchain.com/docs/
- **LangGraph Docs:** https://langchain-ai.github.io/langgraph/
- **BeautifulSoup:** https://www.crummy.com/software/BeautifulSoup/bs4/doc/
- **Pytest:** https://docs.pytest.org/
- **Google Cloud:** https://cloud.google.com/docs

---

## Contact

**Questions or Issues?**
- Check `/docs` folder first
- Review existing similar code
- Search GitHub issues
- Ask project owner: Chris Teuschler

---

**Last Updated:** December 22, 2025
**Project Version:** 1.0
**Python Version:** 3.12
**AI Model:** GPT-5.2
