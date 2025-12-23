# Model Evaluations (Evals) Implementation Plan

## Overview

Implement a model evaluation framework to ensure the Family Planner agent maintains high-quality recommendations as the system evolves. Traditional unit tests are insufficient for agentic systems due to non-determinism and emergent behavior.

## Background: Why Traditional Testing Fails for Agents

### The Problem
```
Traditional Software          Agentic Systems
┌─────────────┐              ┌─────────────┐
│     E2E     │              │    Evals    │  ← Most important!
├─────────────┤              ├─────────────┤
│ Integration │              │ Integration │
├─────────────┤              ├─────────────┤
│    Unit     │  ← Most      │  Contracts  │
└─────────────┘              └─────────────┘
```

**Why Traditional Tests Fail:**
1. **Non-determinism**: Same input → different output (LLM variance)
2. **Tool orchestration**: Care about "did it achieve the goal?" not "did it call function X?"
3. **Emergent behavior**: Agent might find creative solutions you didn't anticipate
4. **Quality vs. Correctness**: Output can be "correct" but low quality

## Testing Strategy

### Level 1: Contract Tests ✅ (Already Implemented)

**Purpose**: Verify tools are wired correctly

**Location**: `tests/test_family_manager.py`

**Examples**:
```python
def test_tools_list_has_only_event_fetchers():
    """Verify all 6 event scrapers are registered"""
    assert len(tools) == 6

def test_create_messages_includes_weather_in_prompt():
    """Verify weather is pre-fetched into context"""
    assert "weather" in system_prompt
```

✅ **Keep these** - Fast, deterministic, catch broken imports/wiring.

---

### Level 2: Model Evals 🔨 (TO BE IMPLEMENTED)

**Purpose**: Evaluate if the agent achieves user goals

**Status**: Not Started

---

## Implementation Tasks

### Task 1: Create Evals Infrastructure

**Status**: Not Started
**Priority**: High
**Estimated Time**: 1-2 hours

#### Deliverables

1. **Create directory structure**:
```bash
evals/
├── __init__.py
├── llm_grader.py          # LLM-as-judge implementation
├── test_agent_evals.py    # Family planner eval tests
├── test_scraper_evals.py  # Scraper quality evals
└── fixtures/
    └── sample_outputs.json # Known good outputs for regression testing
```

2. **Implement LLM Grader** (`evals/llm_grader.py`):

```python
"""
LLM-as-Judge Pattern

Uses a small, fast LLM (gpt-4o-mini) to grade agent outputs based on criteria.
This is more reliable than regex/keyword matching for evaluating natural language.
"""

from langchain.chat_models import init_chat_model
import json
from typing import Dict, Any


class LLMGrader:
    """Use LLM to grade agent outputs against criteria"""

    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0):
        """
        Initialize grader with specific model.

        Args:
            model: Model to use for grading (default: gpt-4o-mini for speed/cost)
            temperature: 0 for deterministic grading
        """
        self.llm = init_chat_model(model, temperature=temperature)

    def grade(self, criteria: str, output: str, context: Dict[str, Any] = None) -> Dict:
        """
        Grade an output against criteria.

        Args:
            criteria: What to evaluate (markdown format)
            output: The agent's output to grade
            context: Optional context (weather, children info, etc.)

        Returns:
            {
                "passes": bool,
                "score": int (0-100),
                "reasoning": str,
                "evidence": str (quote from output)
            }
        """
        context_str = ""
        if context:
            context_str = f"\n\nCONTEXT:\n{json.dumps(context, indent=2)}\n"

        prompt = f"""You are evaluating an AI agent's output.

EVALUATION CRITERIA:
{criteria}
{context_str}
AGENT OUTPUT:
{output}

Evaluate the output and return ONLY valid JSON (no markdown):
{{
  "passes": true or false,
  "score": 0-100,
  "reasoning": "brief explanation of your evaluation",
  "evidence": "relevant quote from output supporting your decision"
}}
"""

        response = self.llm.invoke(prompt)

        # Extract content and clean up
        content = response.content if hasattr(response, 'content') else str(response)
        content = content.strip()

        # Remove markdown code blocks if present
        if content.startswith('```json'):
            content = content[7:]
        if content.startswith('```'):
            content = content[3:]
        if content.endswith('```'):
            content = content[:-3]
        content = content.strip()

        return json.loads(content)


# Convenience function
def grade_output(criteria: str, output: str, context: Dict = None) -> Dict:
    """Grade an output using default LLM grader"""
    grader = LLMGrader()
    return grader.grade(criteria, output, context)
```

3. **Add pytest markers** (`pytest.ini`):

```ini
[pytest]
markers =
    eval: model evaluation tests (may hit OpenAI API, slower)
    slow: slow tests that hit live websites
    integration: integration tests
```

---

### Task 2: Implement Family Planner Evals

**Status**: Not Started
**Priority**: High
**Estimated Time**: 2-3 hours

#### Deliverables

Create `evals/test_agent_evals.py` with these eval tests:

#### Eval 2.1: Weather-Appropriate Venue Selection

```python
import pytest
from unittest.mock import patch
from family_manager import graph_builder
from evals.llm_grader import grade_output


class TestFamilyPlannerEvals:
    """Model-graded evaluations for family planner agent"""

    @pytest.mark.eval
    def test_rainy_day_suggests_indoor_venues(self):
        """
        GOAL: Agent should prioritize indoor venues during bad weather

        GIVEN: Heavy rain forecast
        WHEN: Agent generates recommendations
        THEN: Should suggest Franklin Park Conservatory (indoor)
              Should avoid outdoor-only venues
        """
        # Mock weather to return rainy forecast
        with patch('family_manager.get_weekend_forecast') as mock_weather:
            mock_weather.invoke.return_value = """
            Heavy rain expected all weekend
            Saturday: Rain, 45°F, 95% humidity
            Sunday: Thunderstorms, 50°F
            """

            # Run the agent
            result = graph_builder.invoke({"messages": []})
            output = result["messages"][-1]["content"]

            # Grade with LLM
            criteria = """
            Does the recommendation prioritize indoor venues for rainy weather?

            PASS if:
            - Mentions Franklin Park Conservatory (indoor venue)
            - Acknowledges the rain/bad weather
            - Avoids suggesting outdoor-only activities

            FAIL if:
            - Only suggests outdoor venues (Metro Parks, Lynd Fruit Farm)
            - Ignores weather conditions

            Score 0-100 on weather-appropriateness.
            """

            grade = grade_output(
                criteria=criteria,
                output=output,
                context={
                    "weather": "Heavy rain all weekend",
                    "available_indoor_venues": ["Franklin Park Conservatory", "Olentangy Caverns"]
                }
            )

            assert grade["passes"], f"Failed: {grade['reasoning']}"
            assert grade["score"] >= 80, f"Low score ({grade['score']}): {grade['reasoning']}"
```

#### Eval 2.2: Interest-Based Personalization

```python
    @pytest.mark.eval
    def test_considers_childrens_interests(self):
        """
        GOAL: Recommendations should reflect children's specific interests

        GIVEN: Grayson loves reptiles/snakes, Madeline loves art, Chase loves trains
        WHEN: Agent suggests activities
        THEN: Should mention relevant opportunities (zoo reptiles, conservatory art, etc.)
        """
        result = graph_builder.invoke({"messages": []})
        output = result["messages"][-1]["content"]

        criteria = """
        Does the recommendation show awareness of children's interests?

        Children's interests:
        - Grayson (age 7): reptiles, snakes, nature, animals, art, science
        - Madeline (age 6): art, dancing, animals
        - Chase (age 3): trucks, trains, animals, playgrounds

        PASS if:
        - Mentions at least ONE interest-aligned activity per child
        - Examples: Zoo reptile exhibits for Grayson, art programs at Conservatory for Madeline, train-related for Chase

        Score 0-100 on personalization quality.
        """

        from family_config import CHILDREN

        grade = grade_output(
            criteria=criteria,
            output=output,
            context={"children": CHILDREN}
        )

        # More lenient - not all interests need to match, just show awareness
        assert grade["score"] >= 60, f"Low personalization ({grade['score']}): {grade['reasoning']}"
```

#### Eval 2.3: Age-Appropriate Activities

```python
    @pytest.mark.eval
    def test_age_appropriate_activities(self):
        """
        GOAL: Activities should be suitable for ages 3, 6, and 7

        GIVEN: Children ages 3-7 with 8pm bedtime
        WHEN: Agent suggests activities
        THEN: Should not suggest late-night events, age-restricted activities, or too advanced
        """
        result = graph_builder.invoke({"messages": []})
        output = result["messages"][-1]["content"]

        criteria = """
        Are the suggested activities age-appropriate for children ages 3, 6, and 7?

        PASS if:
        - No activities that are 21+ only
        - No late-night events (past 8pm bedtime)
        - Activities suitable for toddler (age 3) attention span
        - No activities requiring skills beyond age range (rock climbing, long hikes, etc.)

        FAIL if:
        - Suggests adult-only events
        - Events past bedtime
        - Too advanced/dangerous for young children

        Score 0-100 on age-appropriateness.
        """

        grade = grade_output(
            criteria=criteria,
            output=output,
            context={"ages": [7, 6, 3], "bedtime": "8pm"}
        )

        assert grade["passes"], f"Age-inappropriate: {grade['reasoning']}"
        assert grade["score"] >= 85, f"Score too low: {grade['score']}"
```

#### Eval 2.4: Output Format Quality

```python
    @pytest.mark.eval
    def test_suggests_three_activities_with_details(self):
        """
        GOAL: Output should be well-formatted with 3 distinct activities

        GIVEN: Agent generates recommendations
        WHEN: Output is examined
        THEN: Should have 3 activities with venue, description, why it's good for family
        """
        result = graph_builder.invoke({"messages": []})
        output = result["messages"][-1]["content"]

        criteria = """
        Does the output contain 3 well-described family activities?

        PASS if:
        - Lists exactly 3 distinct activities
        - Each has: venue name, brief description, why it's good for this family
        - Clear formatting (numbered list or clear sections)

        FAIL if:
        - Fewer than 3 activities
        - Vague descriptions ("go to zoo" without details)
        - Poor formatting (hard to distinguish activities)

        Score 0-100 on output quality.
        """

        grade = grade_output(criteria=criteria, output=output)

        assert grade["passes"], f"Poor formatting: {grade['reasoning']}"
        assert grade["score"] >= 75
```

#### Eval 2.5: Tool Usage Correctness

```python
    @pytest.mark.eval
    def test_calls_appropriate_event_scrapers(self):
        """
        GOAL: Agent should use event scraper tools to get current information

        GIVEN: Agent has access to 6 event scraper tools
        WHEN: Generating recommendations
        THEN: Should call at least 2-3 scrapers to gather event info
        """
        # This requires inspecting the agent's tool calls
        # We can check the intermediate messages for tool invocations

        result = graph_builder.invoke({"messages": []})

        # Extract tool calls from message history
        tool_calls = []
        for msg in result.get("messages", []):
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                tool_calls.extend([tc.name for tc in msg.tool_calls])

        # Should call at least 2 event scrapers
        event_scraper_calls = [
            name for name in tool_calls
            if "events" in name or "caverns" in name or "wilds" in name
        ]

        assert len(event_scraper_calls) >= 2, \
            f"Agent only called {len(event_scraper_calls)} scrapers: {event_scraper_calls}"
```

---

### Task 3: Implement Scraper Quality Evals

**Status**: Not Started
**Priority**: Medium
**Estimated Time**: 1-2 hours

#### Deliverables

Create `evals/test_scraper_evals.py`:

```python
import pytest
import json
from evals.llm_grader import grade_output
from event_scrapers import (
    get_conservatory_events,
    get_olentangy_caverns_info,
    get_wilds_events,
)


class TestScraperQualityEvals:
    """Evaluate AI scraper output quality"""

    @pytest.mark.eval
    @pytest.mark.slow
    def test_conservatory_scraper_extracts_coherent_data(self):
        """
        GOAL: Conservatory scraper returns valid, coherent event data

        WHEN: Scraper runs against live website
        THEN: Should extract events with valid titles, dates, descriptions
        """
        result = get_conservatory_events()

        # Should be valid JSON
        try:
            events = json.loads(result)
        except json.JSONDecodeError:
            pytest.fail(f"Scraper returned invalid JSON: {result[:500]}")

        # Should find at least one event
        assert isinstance(events, list), "Result should be list of events"

        if len(events) == 0:
            pytest.skip("No events currently listed on website")

        # Grade first event quality with LLM
        event = events[0]

        criteria = """
        Is this scraped event data valid and coherent?

        PASS if:
        - Title is a real event name (not HTML tags, not "undefined")
        - Date is in recognizable format (e.g., "Jan 4", "January 4-6", etc.)
        - Venue is "Franklin Park Conservatory"
        - Description (if present) is coherent English text

        FAIL if:
        - Title is HTML/garbage ("</div>", "null", etc.)
        - Date is missing or invalid ("undefined", "NaN")
        - Data looks corrupted

        Score 0-100 on data quality.
        """

        grade = grade_output(
            criteria=criteria,
            output=json.dumps(event, indent=2)
        )

        assert grade["passes"], f"Poor data quality: {grade['reasoning']}\nEvent: {event}"
        assert grade["score"] >= 70, f"Quality score too low: {grade['score']}"

    @pytest.mark.eval
    def test_all_scrapers_return_valid_json(self):
        """All AI scrapers should return parseable JSON"""
        scrapers = {
            "conservatory": get_conservatory_events,
            "olentangy_caverns": get_olentangy_caverns_info,
            "wilds": get_wilds_events,
        }

        for name, scraper in scrapers.items():
            result = scraper()

            try:
                data = json.loads(result)
                assert isinstance(data, (list, dict)), \
                    f"{name} returned JSON but not list/dict: {type(data)}"
            except json.JSONDecodeError as e:
                pytest.fail(
                    f"{name} scraper returned invalid JSON:\n"
                    f"Error: {e}\n"
                    f"Output: {result[:500]}"
                )

    @pytest.mark.eval
    @pytest.mark.slow
    def test_scrapers_handle_errors_gracefully(self):
        """Scrapers should return error JSON, not crash"""
        # This would require mocking failed HTTP requests
        # or testing against intentionally broken URLs
        pass  # TODO: Implement error handling tests
```

---

### Task 4: Set Up Automated Eval Runs

**Status**: Not Started
**Priority**: Low (can run manually first)
**Estimated Time**: 1 hour

#### Deliverables

1. **GitHub Actions Workflow** (`.github/workflows/weekly-evals.yml`):

```yaml
name: Weekly Model Evals

on:
  schedule:
    # Run every Monday at 10am UTC
    - cron: '0 10 * * 1'
  workflow_dispatch:  # Allow manual trigger

jobs:
  run-evals:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-json-report

      - name: Run model evals
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        run: |
          pytest evals/ -m eval -v \
            --json-report --json-report-file=eval-results.json

      - name: Upload results
        uses: actions/upload-artifact@v3
        with:
          name: eval-results
          path: eval-results.json

      - name: Check for regressions
        run: |
          # TODO: Compare scores to baseline
          # Alert if scores drop significantly
          python scripts/check_eval_regression.py
```

2. **Regression Checker** (`scripts/check_eval_regression.py`):

```python
"""
Check if eval scores have regressed compared to baseline.

Baseline scores are stored in evals/baseline_scores.json
This script compares current run to baseline and fails if regression detected.
"""

import json
import sys

REGRESSION_THRESHOLD = 10  # Alert if score drops by more than 10 points


def load_baseline():
    """Load baseline eval scores"""
    try:
        with open('evals/baseline_scores.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("No baseline found - this will become the baseline")
        return {}


def load_current_results():
    """Load results from current eval run"""
    with open('eval-results.json', 'r') as f:
        return json.load(f)


def check_regression(baseline, current):
    """Compare current scores to baseline"""
    regressions = []

    for test_name, current_score in current.items():
        if test_name not in baseline:
            print(f"NEW TEST: {test_name} = {current_score}")
            continue

        baseline_score = baseline[test_name]
        diff = current_score - baseline_score

        if diff < -REGRESSION_THRESHOLD:
            regressions.append({
                "test": test_name,
                "baseline": baseline_score,
                "current": current_score,
                "diff": diff
            })

    return regressions


if __name__ == "__main__":
    baseline = load_baseline()
    current = load_current_results()

    regressions = check_regression(baseline, current)

    if regressions:
        print("⚠️  REGRESSION DETECTED!")
        for reg in regressions:
            print(f"  {reg['test']}: {reg['baseline']} → {reg['current']} ({reg['diff']:+.1f})")
        sys.exit(1)
    else:
        print("✅ No regressions detected")
        sys.exit(0)
```

---

## Running Evals

### Manual Execution

```bash
# Run all evals
pytest evals/ -m eval -v

# Run only agent evals
pytest evals/test_agent_evals.py -m eval -v

# Run only fast evals (skip slow scraper tests)
pytest evals/ -m "eval and not slow" -v

# Run single eval
pytest evals/test_agent_evals.py::TestFamilyPlannerEvals::test_rainy_day_suggests_indoor_venues -v
```

### Interpreting Results

```bash
# Example output:
evals/test_agent_evals.py::test_rainy_day_suggests_indoor_venues PASSED
  Grade: {"passes": true, "score": 92, "reasoning": "Correctly prioritized Franklin Park Conservatory..."}

evals/test_agent_evals.py::test_considers_childrens_interests FAILED
  Grade: {"passes": false, "score": 45, "reasoning": "Did not mention reptile exhibits for Grayson"}
```

**When evals fail:**
1. Check the reasoning - is it a real issue or LLM grader being too strict?
2. Review the evidence quote - what specifically failed?
3. Decide: Fix the agent, or adjust the eval criteria?

---

## Success Metrics

### Phase 1: Basic Coverage (Week 1)
- ✅ 5 agent evals implemented
- ✅ 3 scraper evals implemented
- ✅ Can run manually with `pytest evals/`
- ✅ Baseline scores established

### Phase 2: Automation (Week 2-3)
- ✅ GitHub Actions workflow running weekly
- ✅ Regression detection working
- ✅ Results stored/tracked over time

### Phase 3: Continuous Improvement (Ongoing)
- Track eval scores in dashboard (BrainTrust/LangSmith)
- A/B test prompt improvements
- Add evals for new features
- Achieve >85 average score across all evals

---

## Integration with Existing Tests

```bash
# Current test structure
tests/
├── test_family_config.py     # Unit tests (family data)
└── test_family_manager.py    # Contract tests (tools wired correctly)

# After evals implementation
tests/                         # Contract tests (fast, deterministic)
├── test_family_config.py
└── test_family_manager.py

evals/                         # Model evals (slower, LLM-graded)
├── llm_grader.py
├── test_agent_evals.py
├── test_scraper_evals.py
└── fixtures/
```

**Run everything**:
```bash
pytest tests/ evals/ -v
```

**Run only fast tests (CI)**:
```bash
pytest tests/ -v  # Excludes evals/
```

**Run only evals (weekly)**:
```bash
pytest evals/ -m eval -v
```

---

## Cost Considerations

**Estimated costs per eval run:**
- 5 agent evals × ~2K tokens each = 10K tokens
- 3 scraper evals × ~1K tokens each = 3K tokens
- **Total: ~13K tokens/run**
- **Cost: ~$0.01/run** with gpt-4o-mini

**Weekly runs**: ~$0.50/year
**Daily runs**: ~$3.65/year

**Very affordable for quality assurance!**

---

## References

- [Anthropic: Evaluating AI Systems](https://docs.anthropic.com/en/docs/build-with-claude/develop-tests)
- [OpenAI: Evals Framework](https://github.com/openai/evals)
- [BrainTrust: LLM Evals Platform](https://www.braintrust.dev/)
- [LangSmith: Evaluation](https://docs.smith.langchain.com/evaluation)
- [Hamel Husain: LLM Evals Guide](https://hamel.dev/blog/posts/evals/)

---

## Next Steps

1. ✅ **This PR**: Document evals approach (this file)
2. 🔨 **Next PR**: Implement `evals/llm_grader.py` + 3 basic agent evals
3. 🔨 **Future PR**: Add scraper evals + automated weekly runs
4. 🔨 **Future PR**: Integrate with BrainTrust or LangSmith for tracking
