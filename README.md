# 🧭 Weekend Planning Assistant (AI Agentic App)

This project is a **Generative AI-based assistant** that helps families decide what to do on the weekend. It uses a **LangChain agentic workflow**, enhanced by real-time weather data, family preferences, and local event information.

---

## ✨ Features

- 🧠 Conversational planning via LLM (e.g., GPT-4)
- 🌦 Weather-aware activity suggestions
- 🗓 Calendar- and availability-aware recommendations
- 📍 Event lookups from real-world APIs
  - [x] Event lookup for Columbus Metro Parks
  - [x] TODO: Event lookup for Columbus Zoo
  - [ ] TODO: Event lookup for The Wilds
  - [ ] TODO: Event lookup for COSI
  - [ ] TODO: Event lookup for Franklin County Conservatory
- 👨‍👩‍👧 Personalized based on family preferences and feedback
- ⚙️ Modular agent/tool design using LangChain

---

## 🏗 Architecture

```mermaid
graph TD
  subgraph UI Layer
    A[User: What should we do this weekend?]
  end

  subgraph Agentic Core
    LLM[LLM GPT-4 via ChatOpenAI]
    LLM --> M[Conversation Memory]
    LLM --> T1[Tool: WeatherForecast]
    LLM --> T2[Tool: UserPreferences]
    LLM --> T3[Tool: LocalEvents]
  end

  subgraph Tool Implementations
    T1 --> W[Weather API e.g., OpenWeatherKit]
    T2 --> P[Vector DB / Profile Store]
    T3 --> E[Event APIs Eventbrite, Google Places]
  end

  A -->|Prompt| LLM
  LLM -->|Tool Calls| T1
  LLM --> T2
  LLM --> T3
  T1 -->|Weather Data| LLM
  T2 -->|User Preferences| LLM
  T3 -->|Event Options| LLM
  LLM -->|Final Recommendation| A
```

---

## 🧩 HTML Parser Agent

The project includes an **HTML Parser Agent** (`html_parser_agent.py`) that accelerates the process of extracting event information from new websites. This tool fetches relevant HTML content (such as the `<main>` tag or event containers) and can generate Python parser code to extract structured event data. It is especially useful for quickly adapting the assistant to new event sources, reducing manual effort and boilerplate when integrating new event feeds.

- 🚀 Rapidly generate event parsers for new sites
- 🛠️ Extracts and returns only the most relevant HTML for event listings
- 🤖 Can auto-generate Python code to parse event data into structured formats
