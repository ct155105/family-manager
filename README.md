# 🧭 Weekend Planning Assistant (AI Agentic App)

This project is a **Generative AI-based assistant** that helps families decide what to do on the weekend. It uses a **LangChain agentic workflow**, enhanced by real-time weather data, family preferences, and local event information.

---

## ✨ Features

- 🧠 Conversational planning via LLM (e.g., GPT-4)
- 🌦 Weather-aware activity suggestions
- 🗓 Calendar- and availability-aware recommendations
- 📍 Event lookups from real-world APIs
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
