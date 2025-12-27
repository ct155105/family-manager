# Family Manager Documentation

This directory contains comprehensive documentation for the Family Manager project, organized into logical groups for easy reference.

## Documentation Index

### 01. Personalization and State Management
**File:** `01-personalization-and-state.md` | **Status:** ✅ COMPLETED

**Topics Covered:**
- Dynamic children age calculation
- Children interests data store
- Recommendation history database (Firestore)
- Configuration management approach

**Related Files:**
- `FIRESTORE_SETUP.md` - Setup guide for Firestore with ADC
- `AGENT_STATE_PATTERNS.md` - Deep dive into state patterns for agents
- `TASK3_IMPLEMENTATION_SUMMARY.md` - Quick reference for Task #3

**Use When:**
- Implementing dynamic family profiles
- Setting up data persistence
- Working on personalization features
- Learning about agent state management patterns

---

### 02. Event Scrapers Implementation
**File:** `02-event-scrapers.md`

**Topics Covered:**
- Current and planned event scrapers
- Standard scraper implementation pattern
- Venue details (URLs, distances, notes)
- Weather-dependent recommendation logic
- Testing and error handling strategies

**Use When:**
- Adding new venue scrapers
- Understanding scraper architecture
- Planning Ohio attractions coverage

**Venues Documented:**
- Franklin Park Conservatory
- Olentangy Caverns
- The Wilds
- Cincinnati Zoo
- Newport Aquarium
- Wright-Patterson Air Force Museum
- Kings Island
- Hocking Hills
- Plus research items (COSI, Cedar Point, etc.)

---

### 03. AI Agent Improvements
**File:** `03-ai-improvements.md`

**Topics Covered:**
- Current agent configuration
- Using recommendation history to avoid repeats
- Top 3 recommendations logic
- Enhanced system prompts
- Reasoning effort configuration
- Quality evaluation metrics

**Use When:**
- Improving recommendation quality
- Adjusting AI behavior
- Implementing ranking logic
- Integrating with recommendation history

---

### 04. GCP Deployment Architecture
**File:** `04-deployment-architecture.md`

**Topics Covered:**
- Cloud architecture design (Cloud Run, Firestore, Secret Manager)
- Deployment configurations (Dockerfile, Cloud Build, Terraform)
- IAM and security setup
- Monitoring and observability
- Cost estimates
- Deployment procedures

**Use When:**
- Deploying to production
- Setting up GCP infrastructure
- Implementing secrets management
- Configuring scheduled execution
- Planning costs and scaling

---

## Quick Start Guide

### For Local Development
1. Review `01-personalization-and-state.md` for family config setup
2. Check `02-event-scrapers.md` for adding new venues
3. Reference `03-ai-improvements.md` for tuning recommendations

### For Production Deployment
1. Start with `04-deployment-architecture.md`
2. Follow setup scripts in order
3. Configure secrets as documented
4. Test manually before enabling scheduler

---

## Task Priorities

### Phase 1: Immediate Improvements ✅ COMPLETED
1. ✅ Fix weather location bug (Columbus, OH vs GA)
2. ✅ Update to latest OpenAI model (GPT-5.2)
3. ✅ Dynamic children ages (`01-personalization-and-state.md`, Task #1)
4. ✅ Children interests store (`01-personalization-and-state.md`, Task #2)

### Phase 2: Personalization & State ✅ COMPLETED
5. ✅ Firestore schema design (`01-personalization-and-state.md`, Task #3)
6. ✅ Recommendation history with state hydration
7. ✅ ADC authentication for local development

### Phase 3: Expand Coverage (IN PROGRESS)
8. ✅ Franklin Park Conservatory scraper
9. ✅ Air Force Museum scraper
10. ✅ 10 venue scrapers implemented
11. **→ COSI scraper** (`02-event-scrapers.md`)
12. **→ Cedar Point scraper** (`02-event-scrapers.md`)

### Phase 4: Production Ready
13. **→ GCP architecture** (`04-deployment-architecture.md`)
14. **→ Deployment configs** (`04-deployment-architecture.md`)
15. **→ Deploy to GCP** (`04-deployment-architecture.md`)

---

## Document Maintenance

### When to Update These Docs

**After completing a task:**
- Mark task as complete in relevant doc
- Add any implementation notes or gotchas
- Update architecture diagrams if changed

**When adding new venues:**
- Update `02-event-scrapers.md` with venue details
- Add to integration checklist

**When modifying AI logic:**
- Update system prompts in `03-ai-improvements.md`
- Document any new tools or parameters

**When changing deployment:**
- Update architecture diagrams in `04-deployment-architecture.md`
- Revise cost estimates
- Update deployment scripts

---

## Contributing

When working on this project:
1. Read the relevant doc file before starting
2. Update docs as you implement changes
3. Keep examples and code snippets current
4. Add lessons learned to appropriate sections

---

## Architecture Diagrams

See individual doc files for:
- `01-personalization-and-state.md`: Database schema
- `03-ai-improvements.md`: Agent decision flow
- `04-deployment-architecture.md`: GCP component architecture

---

## Contact & Support

**Project Owner:** Chris Teuschler  
**Repository:** github.com/ct155105/family-manager  
**Documentation Version:** 1.0 (December 2025)

---

## Related Files

**Core Application:**
- `/README.md` - Project overview and running instructions
- `/family_manager.py` - Main LangGraph pipeline
- `/recommendation_db.py` - Firestore state management
- `/family_config.py` - Family configuration (ages, interests)
- `/weather_forecaster.py` - Weather tool

**Event Scrapers:**
- `/event_scrapers/` - All venue scrapers (10+ implementations)

**Tests:**
- `/tests/test_firestore_connection.py` - Firestore integration test
- `/tests/test_family_config.py` - Family config tests

**Configuration:**
- `/requirements.txt` - Python dependencies
- `/.env` - Environment variables (not in git)
