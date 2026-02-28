# ✈️ Lufthansa Business Travel Buddy

> Proactive disruption manager for Lufthansa business travelers

**Built for:** Hamburg Hackathon: Innovate the Skies & Beyond (Feb 28, 2026)  
**Team:** [Your Team Name]  
**Tech:** Gemini 3.0 + Google Search Grounding + ADK

---

## 🎯 The Problem

When a flight is delayed or canceled, **the flight itself is only 10% of the problem**. The other 90% is the downstream dependencies:
- Missed meetings
- Client notifications
- Schedule cascades
- Rebooking complexity

Business travelers (12-15% of passengers) generate **50-75% of airline profits**. They need proactive solutions, not reactive scrambling.

---

## 💡 The Solution

Lufthansa Business Travel Buddy is an AI-powered assistant that:

1. **Monitors** your Lufthansa booking for disruptions
2. **Finds** alternative flights (business class priority)
3. **Analyzes** calendar impact (which meetings are at risk?)
4. **Drafts** professional notifications (emails ready to send)

All in **one conversation**, powered by Gemini's reasoning capabilities.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│              COORDINATOR AGENT (ReAct)                  │
│  THOUGHT → ACTION → OBSERVATION → THOUGHT → ...        │
└──────────────────────────┬──────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┬────────────┐
         ▼                 ▼                 ▼            ▼
┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐
│   Flight    │  │  Calendar   │  │   Comms     │  │  Search   │
│   Tools     │  │   Tools     │  │   Tools     │  │ Grounding │
└─────────────┘  └─────────────┘  └─────────────┘  └───────────┘
```

**Design Pattern:** Coordinator + ReAct
- ReAct for dynamic reasoning about disruption severity
- Coordinator orchestrates specialized tools

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Gemini API key ([get one here](https://ai.google.dev))
- Aviationstack API key ([free tier](https://aviationstack.com/signup))

### Installation

```bash
# Clone the repository
git clone https://github.com/your-team/lufthansa-travel-buddy.git
cd lufthansa-travel-buddy

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install poetry
poetry install

# Configure environment
cp .env.example .env
# Edit .env with your API keys
```

### Run the Agent

```bash
# Interactive terminal
adk run travel_buddy

# Web UI (recommended for demos)
adk web
# Open http://localhost:8000 and select "travel_buddy"
```

---

## 🎮 Demo Scenario

```
User: My booking is LH-ABC123, flying from Hamburg to New York today.
      Can you check if there are any issues?

Agent: 
🚨 DISRUPTION ALERT: Your LH456 is delayed 90 minutes

⚠️ IMPACT: You will miss your JFK connection (LH404)

✈️ RECOMMENDED REBOOKING:
   LH2042 HAM→JFK (Direct) | Departs 10:30 | Arrives 18:00 EST
   → Preserves your 16:00 board meeting ✓
   → Business Class confirmed
   
📅 CALENDAR IMPACT:
   ✓ 16:00 Board meeting — ON TRACK with LH2042
   ⚠️ 19:00 Client dinner — suggest 19:30

📧 DRAFT NOTIFICATIONS:
   • Email to CEO: Delay notice + confirmation attending
   • Email to Client: Dinner time adjustment
```

---

## 📁 Project Structure

```
lufthansa-travel-buddy/
├── travel_buddy/              # Main agent package
│   ├── __init__.py           # Exports root_agent (required by ADK)
│   ├── agent.py              # Root agent definition
│   ├── config.py             # Environment configuration
│   ├── prompts.py            # System prompts
│   └── sub_agents/           # Domain-specific tools
│       ├── flight/           # Flight status & rebooking
│       ├── calendar/         # Calendar integration
│       └── comms/            # Email drafting
├── tests/                    # Unit tests
├── eval/                     # Evaluation datasets
└── deployment/               # Vertex AI deployment
```

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| LLM | Gemini 3 Flash |
| Framework | Google Agent Development Kit (ADK) |
| Real-time Data | Google Search Grounding |
| **Flight API** | **Lufthansa Open API** ✈️ |
| Calendar | Google Calendar MCP (TODO) |

### Lufthansa API Endpoints Used

| Endpoint | Purpose |
|----------|---------|
| `/operations/flightstatus/{flight}/{date}` | Real-time flight status |
| `/operations/flightstatus/route/{origin}/{dest}/{date}` | Route-based flight search |
| `/operations/flightstatus/departures/{airport}/{time}` | Airport departures |
| `/operations/flightstatus/arrivals/{airport}/{time}` | Airport arrivals |

---

## 📊 Business Value

| Metric | Impact |
|--------|--------|
| Target Segment | Business travelers (12-15% of pax) |
| Revenue Impact | 50-75% of airline profits |
| Problem Solved | Ripple effect of disruptions |
| Time Saved | ~30 min per disruption event |

---

## 🏆 Hackathon Highlights

- **Real-time data integration**: Live flight status via APIs
- **Search Grounding**: Weather, strikes, airport news
- **ReAct reasoning**: Transparent decision-making process
- **End-to-end workflow**: From alert to action in one conversation

---

## 📝 License

MIT License - Built for Hamburg Hackathon 2026

---

## 👥 Team

- [Team Member 1] - Role
- [Team Member 2] - Role
- [Team Member 3] - Role
