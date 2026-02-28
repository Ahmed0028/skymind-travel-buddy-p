# skymind-travel-buddy-p
hamburg hackathon : Agent AI
# Lufthansa Business Travel Buddy — ADK Project Structure

## Overview

This document explains the project structure for the Lufthansa Business Travel Buddy agent, built using Google's Agent Development Kit (ADK).

---

# Google Cloud Platform (GCP) Project Infrastructure

This document outlines the cloud services enabled for the Gemini AI project. These services provide the foundation for model hosting, application deployment, and data storage.

## Project Configuration

- **Environment:** Development / Production
- **Region:** `us-central1` (Recommended for Vertex AI)
- **Authentication:** Application Default Credentials (ADC)

---

### 🚀 Core AI & Compute Services

| Service Name | API Identifier | Purpose |
| :--- | :--- | :--- |
| **Vertex AI** | `aiplatform.googleapis.com` | Primary interface for Gemini 1.5/2.0 models, tuning, and vector search. |
| **Cloud Run** | `run.googleapis.com` | Serverless environment to host the application frontend/backend. |
| **Compute Engine** | `compute.googleapis.com` | Underlying VM infrastructure for specialized workloads. |

### 🛠️ DevOps & CI/CD

| Service Name | API Identifier | Purpose |
| :--- | :--- | :--- |
| **Cloud Build** | `cloudbuild.googleapis.com` | Automates container builds and deployment pipelines. |
| **Artifact Registry** | `artifactregistry.googleapis.com` | Secure storage for Docker container images. |

### 📂 Storage & Databases

| Service Name | API Identifier | Purpose |
| :--- | :--- | :--- |
| **Cloud Spanner** | `spanner.googleapis.com` | Globally scalable relational database for high-consistency data. |
| **Cloud Storage** | `storage.googleapis.com` | Object storage for training datasets, PDF files for RAG, and backups. |

---

## Setup Instructions

### 1. Enable Services via CLI
To re-enable or verify these services in a new project, run:
```bash
gcloud services enable \
  compute.googleapis.com \
  aiplatform.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  spanner.googleapis.com \
  storage.googleapis.com

## Project Structure

```
lufthansa-travel-buddy/
│
├── README.md                          # Project overview and setup instructions
├── pyproject.toml                     # Poetry/pip dependencies and project metadata
├── .env.example                       # Template for environment variables
├── .gitignore                         # Git ignore file
│
├── travel_buddy/                      # Main agent package (ADK requires this structure)
│   │
│   ├── __init__.py                    # Package initializer (exports root_agent)
│   ├── agent.py                       # Root agent definition (REQUIRED by ADK)
│   ├── config.py                      # Configuration and environment variables
│   ├── prompts.py                     # System prompts and instructions
│   │
│   ├── sub_agents/                    # Specialized sub-agents
│   │   ├── __init__.py
│   │   │
│   │   ├── flight/                    # Flight monitoring & rebooking agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Flight agent definition
│   │   │   ├── tools.py               # Flight-related tools (API calls)
│   │   │   └── prompts.py             # Flight agent instructions
│   │   │
│   │   ├── calendar/                  # Calendar integration agent
│   │   │   ├── __init__.py
│   │   │   ├── agent.py               # Calendar agent definition
│   │   │   ├── tools.py               # Calendar tools (Google Calendar MCP)
│   │   │   └── prompts.py             # Calendar agent instructions
│   │   │
│   │   └── comms/                     # Communication drafting agent
│   │       ├── __init__.py
│   │       ├── agent.py               # Comms agent definition
│   │       ├── tools.py               # Email/message drafting tools
│   │       └── prompts.py             # Comms agent instructions
│   │
│   ├── tools/                         # Shared tools across agents
│   │   ├── __init__.py
│   │   ├── aviation_api.py            # Aviationstack/FlightLabs API wrapper
│   │   ├── calendar_mcp.py            # Google Calendar MCP integration
│   │   └── search_grounding.py        # Google Search grounding utilities
│   │
│   ├── shared_libraries/              # Shared utilities and helpers
│   │   ├── __init__.py
│   │   ├── utils.py                   # Common utility functions
│   │   ├── models.py                  # Pydantic models for data validation
│   │   └── constants.py               # Constants (IATA codes, status mappings)
│   │
│   └── callbacks/                     # Event callbacks and hooks
│       ├── __init__.py
│       └── logging_callback.py        # Logging and monitoring callbacks
│
├── tests/                             # Unit and integration tests
│   ├── __init__.py
│   ├── test_flight_agent.py
│   ├── test_calendar_agent.py
│   ├── test_comms_agent.py
│   └── test_integration.py
│
├── eval/                              # Agent evaluation datasets and scripts
│   ├── data/
│   │   └── disruption_scenarios.evalset.json
│   └── run_eval.py
│
└── deployment/                        # Deployment scripts for Vertex AI
    ├── deploy.py                      # Deploy to Vertex AI Agent Engine
    └── test_deployment.py             # Test deployed agent
```

---

## Step-by-Step Explanation

### Step 1: Root Directory Files

#### `pyproject.toml`
```toml
[tool.poetry]
name = "lufthansa-travel-buddy"
version = "0.1.0"
description = "Proactive disruption manager for Lufthansa business travelers"
authors = ["Your Team <team@example.com>"]

[tool.poetry.dependencies]
python = "^3.11"
google-adk = "^1.0.0"
google-genai = "^1.0.0"
requests = "^2.31.0"
pydantic = "^2.0.0"
python-dotenv = "^1.0.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"

[tool.poetry.group.deployment.dependencies]
google-cloud-aiplatform = "^1.50.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"
```

#### `.env.example`
```bash
# Gemini API Configuration
GOOGLE_API_KEY=your-gemini-api-key
GOOGLE_GENAI_USE_VERTEXAI=0  # Set to 1 for Vertex AI

# Google Cloud (if using Vertex AI)
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# Aviation API
AVIATIONSTACK_API_KEY=your-aviationstack-key

# Model Configuration
ROOT_AGENT_MODEL=gemini-3-flash-preview
SUB_AGENT_MODEL=gemini-3-flash-preview
```

---

### Step 2: Main Agent Package (`travel_buddy/`)

#### `travel_buddy/__init__.py`
```python
"""
Lufthansa Business Travel Buddy - ADK Agent Package

This file MUST export `root_agent` for ADK to discover the agent.
"""

from .agent import root_agent

__all__ = ["root_agent"]
```

**Why this matters:** ADK looks for a `root_agent` export in the package's `__init__.py`. Without this, `adk run` and `adk web` commands won't work.

---

#### `travel_buddy/agent.py`
```python
"""
Root Agent Definition - Coordinator with ReAct Pattern

This is the main entry point. The root_agent orchestrates all sub-agents
and tools to handle flight disruptions for business travelers.
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from .config import ROOT_AGENT_MODEL
from .prompts import ROOT_AGENT_INSTRUCTION

# Import sub-agents (as tools, not sub_agents for ReAct pattern)
from .sub_agents.flight.tools import (
    check_flight_status,
    find_alternative_flights,
    get_flight_details,
)
from .sub_agents.calendar.tools import (
    get_calendar_events,
    find_meeting_conflicts,
)
from .sub_agents.comms.tools import (
    draft_delay_notification,
    draft_reschedule_request,
)


# Define the root agent with ReAct pattern
# Tools act as "pseudo-agents" - the coordinator reasons about when to use each
root_agent = Agent(
    model=ROOT_AGENT_MODEL,
    name="lufthansa_travel_buddy",
    description="Proactive disruption manager for Lufthansa business travelers",
    instruction=ROOT_AGENT_INSTRUCTION,
    tools=[
        # Flight domain tools
        check_flight_status,
        find_alternative_flights,
        get_flight_details,
        # Calendar domain tools
        get_calendar_events,
        find_meeting_conflicts,
        # Communication domain tools
        draft_delay_notification,
        draft_reschedule_request,
        # Search Grounding for real-time context
        google_search,
    ],
)
```

**Key concept:** We use tools instead of sub_agents because:
1. ReAct pattern needs the coordinator to reason about tool selection
2. Simpler architecture for hackathon timeframe
3. Tools can be called multiple times in a single turn

---

#### `travel_buddy/config.py`
```python
"""
Configuration Management

Loads environment variables and provides typed configuration.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


def get_env_var(name: str, default: str = None, required: bool = False) -> str:
    """Get environment variable with optional default."""
    value = os.getenv(name, default)
    if required and not value:
        raise ValueError(f"Required environment variable {name} is not set")
    return value


# API Keys
GOOGLE_API_KEY = get_env_var("GOOGLE_API_KEY", required=True)
AVIATIONSTACK_API_KEY = get_env_var("AVIATIONSTACK_API_KEY", required=True)

# Model Configuration
ROOT_AGENT_MODEL = get_env_var("ROOT_AGENT_MODEL", "gemini-3-flash-preview")
SUB_AGENT_MODEL = get_env_var("SUB_AGENT_MODEL", "gemini-3-flash-preview")

# Google Cloud (optional, for Vertex AI deployment)
GOOGLE_CLOUD_PROJECT = get_env_var("GOOGLE_CLOUD_PROJECT")
GOOGLE_CLOUD_LOCATION = get_env_var("GOOGLE_CLOUD_LOCATION", "us-central1")
```

---

#### `travel_buddy/prompts.py`
```python
"""
System Prompts and Instructions

Centralized prompt management for consistent agent behavior.
"""

ROOT_AGENT_INSTRUCTION = """
You are the Lufthansa Business Travel Buddy - a senior executive assistant 
specialized in proactive disruption management for business travelers.

## Your Mission
When a business traveler's flight is disrupted, you solve the RIPPLE EFFECT:
- The flight itself is only 10% of the problem
- The other 90% is downstream dependencies: meetings, clients, colleagues

## ReAct Pattern
For each user request, follow this reasoning pattern:

1. THOUGHT: Assess the situation
   - What is the user's booking ID or flight number?
   - What is the current flight status?
   - How severe is the disruption?

2. ACTION: Gather information
   - Use check_flight_status to get delay/cancellation info
   - Use find_alternative_flights to get rebooking options
   - Use get_calendar_events to see impacted meetings
   - Use google_search for context (weather, strikes, airport status)

3. OBSERVATION: Evaluate impact
   - Which meetings are at risk?
   - Which alternative flight best preserves the schedule?
   - Who needs to be notified?

4. ACTION: Prepare outputs
   - Rank rebooking options by schedule preservation
   - Draft notification emails using draft_delay_notification
   - Suggest meeting reschedules if needed

## Response Format
Always provide:
- 🚨 Clear disruption summary
- ✈️ Top 3 rebooking options (ranked by schedule impact)
- 📅 Calendar impact analysis
- 📧 Ready-to-send notification drafts

## Priorities
1. Schedule preservation (making the meeting is paramount)
2. Business class availability (Senator/HON Circle benefits)
3. Minimum total travel time
4. Miles & More earning optimization

## Tone
Professional, concise, proactive. You are a trusted executive assistant
who anticipates needs and solves problems before they escalate.
"""


FLIGHT_AGENT_INSTRUCTION = """
You are a flight operations specialist. Your job is to:
1. Monitor flight status for delays and cancellations
2. Find alternative routing options
3. Compare options by duration, class availability, and connection risk

Always prioritize:
- Business class availability
- Direct flights over connections
- Lufthansa Group carriers (LH, LX, OS, SN, EW)
"""


CALENDAR_AGENT_INSTRUCTION = """
You are a calendar and schedule analyst. Your job is to:
1. Retrieve the user's calendar events for impact assessment
2. Identify which meetings will be affected by flight changes
3. Suggest new meeting times based on updated arrival

Flag meetings as:
- 🔴 CRITICAL: Cannot be missed (board meetings, client presentations)
- 🟡 IMPORTANT: Should attend if possible
- 🟢 FLEXIBLE: Can be rescheduled easily
"""


COMMS_AGENT_INSTRUCTION = """
You are a professional communications specialist. Your job is to:
1. Draft concise, professional delay notifications
2. Propose meeting reschedule requests
3. Format messages for email, Slack, or SMS

Tone: Professional, apologetic but confident, solution-oriented.
Always include: the problem, the solution, and next steps.
"""
```

---

### Step 3: Sub-Agents Directory (`travel_buddy/sub_agents/`)

#### `travel_buddy/sub_agents/flight/tools.py`
```python
"""
Flight Domain Tools

Tools for checking flight status, finding alternatives, and getting details.
These tools wrap the Aviationstack API.
"""

import requests
from typing import Optional
from google.adk.tools import ToolContext

from ...config import AVIATIONSTACK_API_KEY


BASE_URL = "https://api.aviationstack.com/v1"


def check_flight_status(
    booking_id: str = None,
    flight_iata: str = None,
    tool_context: ToolContext = None,
) -> dict:
    """
    Check the current status of a Lufthansa flight.
    
    Use this tool to get real-time delay and cancellation information.
    
    Args:
        booking_id: Lufthansa booking reference (e.g., "ABC123")
        flight_iata: IATA flight number (e.g., "LH456")
    
    Returns:
        dict: Flight status including delay minutes, gate, terminal
    """
    # In production, would resolve booking_id to flight_iata via Lufthansa API
    if not flight_iata and booking_id:
        # Mock resolution for hackathon
        flight_iata = "LH456"
    
    response = requests.get(
        f"{BASE_URL}/flights",
        params={
            "access_key": AVIATIONSTACK_API_KEY,
            "flight_iata": flight_iata,
        },
    )
    
    data = response.json().get("data", [])
    if not data:
        return {"error": f"No data found for flight {flight_iata}"}
    
    flight = data[0]
    return {
        "flight": flight["flight"]["iata"],
        "airline": flight["airline"]["name"],
        "status": flight["flight_status"],
        "departure": {
            "airport": flight["departure"]["airport"],
            "iata": flight["departure"]["iata"],
            "scheduled": flight["departure"]["scheduled"],
            "estimated": flight["departure"].get("estimated"),
            "delay_minutes": flight["departure"].get("delay", 0),
            "gate": flight["departure"].get("gate"),
            "terminal": flight["departure"].get("terminal"),
        },
        "arrival": {
            "airport": flight["arrival"]["airport"],
            "iata": flight["arrival"]["iata"],
            "scheduled": flight["arrival"]["scheduled"],
            "estimated": flight["arrival"].get("estimated"),
        },
    }


def find_alternative_flights(
    origin: str,
    destination: str,
    date: str,
    preferred_class: str = "business",
    tool_context: ToolContext = None,
) -> list:
    """
    Find alternative Lufthansa flights for rebooking.
    
    Use this tool when a flight is delayed or cancelled and the user
    needs alternative routing options.
    
    Args:
        origin: Departure airport IATA code (e.g., "HAM")
        destination: Arrival airport IATA code (e.g., "JFK")
        date: Travel date in YYYY-MM-DD format
        preferred_class: Cabin class preference ("business" or "economy")
    
    Returns:
        list: Top 3 alternative flights ranked by arrival time
    """
    response = requests.get(
        f"{BASE_URL}/flights",
        params={
            "access_key": AVIATIONSTACK_API_KEY,
            "dep_iata": origin,
            "arr_iata": destination,
            "airline_iata": "LH",  # Lufthansa only
        },
    )
    
    flights = response.json().get("data", [])
    
    # Filter and format alternatives
    alternatives = []
    for f in flights[:5]:  # Limit to 5 for processing
        alternatives.append({
            "flight": f["flight"]["iata"],
            "departure_time": f["departure"]["scheduled"],
            "arrival_time": f["arrival"]["scheduled"],
            "origin": f["departure"]["iata"],
            "destination": f["arrival"]["iata"],
            "status": f["flight_status"],
            "aircraft": f.get("aircraft", {}).get("iata", "Unknown"),
        })
    
    return alternatives[:3]  # Return top 3


def get_flight_details(
    flight_iata: str,
    tool_context: ToolContext = None,
) -> dict:
    """
    Get detailed information about a specific flight.
    
    Args:
        flight_iata: IATA flight number (e.g., "LH456")
    
    Returns:
        dict: Detailed flight information including aircraft type
    """
    response = requests.get(
        f"{BASE_URL}/flights",
        params={
            "access_key": AVIATIONSTACK_API_KEY,
            "flight_iata": flight_iata,
        },
    )
    
    data = response.json().get("data", [])
    if not data:
        return {"error": f"No details found for {flight_iata}"}
    
    return data[0]
```

---

#### `travel_buddy/sub_agents/calendar/tools.py`
```python
"""
Calendar Domain Tools

Tools for reading calendar events and finding conflicts.
In production, these would integrate with Google Calendar MCP.
"""

from typing import Optional
from google.adk.tools import ToolContext


# Mock calendar data for hackathon
MOCK_CALENDAR = {
    "2026-02-28": [
        {
            "id": "evt_001",
            "title": "Board Meeting with CEO",
            "start": "16:00",
            "end": "18:00",
            "location": "NYC Office",
            "priority": "critical",
            "attendees": ["ceo@company.com", "cfo@company.com"],
        },
        {
            "id": "evt_002",
            "title": "Client Dinner - Acme Corp",
            "start": "19:00",
            "end": "21:00",
            "location": "The Capital Grille, NYC",
            "priority": "important",
            "attendees": ["john@acmecorp.com"],
        },
    ],
}


def get_calendar_events(
    date: str,
    user_id: str = "default",
    tool_context: ToolContext = None,
) -> list:
    """
    Retrieve calendar events for a specific date.
    
    Use this tool to see what meetings the user has scheduled
    that might be impacted by flight changes.
    
    Args:
        date: Date in YYYY-MM-DD format
        user_id: User identifier (optional)
    
    Returns:
        list: Calendar events for the specified date
    """
    # In production: call Google Calendar MCP
    # For hackathon: return mock data
    events = MOCK_CALENDAR.get(date, [])
    
    return {
        "date": date,
        "event_count": len(events),
        "events": events,
    }


def find_meeting_conflicts(
    arrival_time: str,
    date: str,
    user_id: str = "default",
    tool_context: ToolContext = None,
) -> dict:
    """
    Identify meetings that conflict with the new arrival time.
    
    Use this tool after finding alternative flights to see which
    meetings will be impacted by the new schedule.
    
    Args:
        arrival_time: New arrival time in HH:MM format (24h)
        date: Date in YYYY-MM-DD format
        user_id: User identifier (optional)
    
    Returns:
        dict: Conflict analysis with impacted and safe meetings
    """
    events = MOCK_CALENDAR.get(date, [])
    
    # Parse arrival time
    arrival_hour = int(arrival_time.split(":")[0])
    
    conflicts = []
    safe = []
    
    for event in events:
        event_start = int(event["start"].split(":")[0])
        
        # Add 1 hour buffer for travel from airport
        if arrival_hour + 1 > event_start:
            conflicts.append({
                **event,
                "status": "at_risk",
                "reason": f"Arrives at {arrival_time}, meeting at {event['start']}",
            })
        else:
            safe.append({
                **event,
                "status": "on_track",
            })
    
    return {
        "arrival_time": arrival_time,
        "conflicts": conflicts,
        "safe": safe,
        "summary": f"{len(conflicts)} meeting(s) at risk, {len(safe)} on track",
    }
```

---

#### `travel_buddy/sub_agents/comms/tools.py`
```python
"""
Communications Domain Tools

Tools for drafting professional notifications and reschedule requests.
"""

from typing import Optional
from google.adk.tools import ToolContext


def draft_delay_notification(
    recipient_email: str,
    recipient_name: str,
    delay_info: str,
    new_arrival: str,
    meeting_impact: str = None,
    tool_context: ToolContext = None,
) -> dict:
    """
    Draft a professional delay notification email.
    
    Use this tool to create ready-to-send emails notifying
    colleagues, clients, or family about flight delays.
    
    Args:
        recipient_email: Email address of recipient
        recipient_name: Name of recipient for personalization
        delay_info: Description of the delay (e.g., "90 minute delay")
        new_arrival: New expected arrival time
        meeting_impact: Optional description of meeting impact
    
    Returns:
        dict: Email draft with subject and body
    """
    subject = f"Travel Update: Flight Delay - New Arrival {new_arrival}"
    
    body = f"""Dear {recipient_name},

I wanted to inform you that my flight has been delayed. Here are the updated details:

**Delay:** {delay_info}
**New Arrival:** {new_arrival}
"""

    if meeting_impact:
        body += f"""
**Impact on Our Meeting:** {meeting_impact}
"""

    body += """
I will keep you updated if there are any further changes. Please let me know if you need to adjust our schedule.

Best regards"""

    return {
        "type": "email",
        "to": recipient_email,
        "subject": subject,
        "body": body,
        "status": "draft",
    }


def draft_reschedule_request(
    recipient_email: str,
    recipient_name: str,
    original_time: str,
    proposed_times: list,
    reason: str,
    tool_context: ToolContext = None,
) -> dict:
    """
    Draft a meeting reschedule request.
    
    Use this tool to propose new meeting times when the original
    time is no longer feasible due to travel changes.
    
    Args:
        recipient_email: Email address of recipient
        recipient_name: Name of recipient
        original_time: Original meeting time
        proposed_times: List of proposed alternative times
        reason: Brief reason for reschedule
    
    Returns:
        dict: Email draft with subject and body
    """
    times_formatted = "\n".join([f"  • {t}" for t in proposed_times])
    
    subject = f"Meeting Reschedule Request: {original_time}"
    
    body = f"""Dear {recipient_name},

Due to {reason}, I need to request a reschedule of our meeting originally planned for {original_time}.

Would any of the following alternative times work for you?

{times_formatted}

I apologize for any inconvenience and appreciate your flexibility.

Best regards"""

    return {
        "type": "email",
        "to": recipient_email,
        "subject": subject,
        "body": body,
        "proposed_times": proposed_times,
        "status": "draft",
    }
```

---

### Step 4: Shared Libraries (`travel_buddy/shared_libraries/`)

#### `travel_buddy/shared_libraries/models.py`
```python
"""
Pydantic Models for Data Validation

Type-safe data structures for flight, calendar, and communication data.
"""

from pydantic import BaseModel
from typing import Optional, List
from enum import Enum
from datetime import datetime


class FlightStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    LANDED = "landed"
    CANCELLED = "cancelled"
    DIVERTED = "diverted"
    DELAYED = "delayed"


class Priority(str, Enum):
    CRITICAL = "critical"
    IMPORTANT = "important"
    FLEXIBLE = "flexible"


class FlightInfo(BaseModel):
    flight_iata: str
    airline: str
    status: FlightStatus
    departure_airport: str
    departure_scheduled: datetime
    departure_estimated: Optional[datetime]
    delay_minutes: int = 0
    arrival_airport: str
    arrival_scheduled: datetime
    arrival_estimated: Optional[datetime]
    gate: Optional[str]
    terminal: Optional[str]


class CalendarEvent(BaseModel):
    id: str
    title: str
    start: str
    end: str
    location: Optional[str]
    priority: Priority
    attendees: List[str] = []


class DisruptionAnalysis(BaseModel):
    booking_id: str
    original_flight: FlightInfo
    delay_severity: str  # "minor", "moderate", "severe"
    alternatives: List[dict]
    impacted_meetings: List[CalendarEvent]
    recommended_action: str
```

---

### Step 5: Running the Agent

#### Terminal Commands

```bash
# 1. Navigate to project directory
cd lufthansa-travel-buddy

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install poetry
poetry install

# 4. Copy and configure environment variables
cp .env.example .env
# Edit .env with your API keys

# 5. Run with ADK CLI (interactive terminal)
adk run travel_buddy

# 6. Run with ADK Web UI (browser-based)
adk web
# Open http://localhost:8000 and select "travel_buddy"

# 7. Run tests
pytest tests/

# 8. Run evaluation
python eval/run_eval.py
```

---

## Key ADK Concepts Explained

### 1. `root_agent` Export
ADK discovers your agent by looking for a `root_agent` variable in your package's `__init__.py`. This is **mandatory**.

### 2. Tools vs Sub-Agents
| Approach | When to Use |
|----------|-------------|
| **Tools** | ReAct pattern, coordinator needs to reason about each call |
| **Sub-Agents** | Delegation pattern, hand off entire conversation to specialist |

For the hackathon, we use **Tools** because our Coordinator + ReAct architecture needs fine-grained control.

### 3. ToolContext
ADK passes a `ToolContext` to every tool function. Use it to:
- Access session state: `tool_context.state["key"]`
- Store results for other tools: `tool_context.state["flight_data"] = result`

### 4. Google Search Grounding
Import and add to tools list:
```python
from google.adk.tools import google_search

root_agent = Agent(
    tools=[google_search, ...],  # Enables real-time web search
)
```

### 5. State Management
Pass data between tools using session state:
```python
def tool_a(tool_context: ToolContext):
    result = do_something()
    tool_context.state["result_from_a"] = result
    return result

def tool_b(tool_context: ToolContext):
    data = tool_context.state.get("result_from_a")
    # Use data from tool_a
```

---

## Next Steps

1. **Copy this structure** to your GitHub repo
2. **Implement tools** with real API calls
3. **Test locally** with `adk run travel_buddy`
4. **Iterate on prompts** based on agent behavior
5. **Add evaluation scenarios** in `eval/data/`

Ready to start coding! 🚀
