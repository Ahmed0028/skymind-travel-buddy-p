"""
Root Agent Definition - Coordinator with ReAct Pattern

This is the main entry point for the Lufthansa Business Travel Buddy.
The root_agent orchestrates all tools to handle flight disruptions
for business travelers using the ReAct (Reason and Act) pattern.

Architecture:
- Single ReAct Coordinator with multiple tools (pseudo-agents)
- Tools provide domain-specific functionality (flight, calendar, comms)
- Google Search Grounding for real-time context

Design Pattern: Coordinator + ReAct
- ReAct: Dynamic reasoning about disruption severity and next steps
- Coordinator: Orchestrates specialized tasks across domains
"""

from google.adk.agents import Agent
from google.adk.tools import google_search

from .config import ROOT_AGENT_MODEL
from .prompts import ROOT_AGENT_INSTRUCTION

# Import domain-specific tools
from .sub_agents.flight.tools import (
    check_flight_status,
    find_alternative_flights,
    get_flight_details,
    get_airport_departures,
    get_airport_arrivals,
)
from .sub_agents.calendar.tools import (
    get_calendar_events,
    find_meeting_conflicts,
)
from .sub_agents.comms.tools import (
    draft_delay_notification,
    draft_reschedule_request,
    send_email,
)


# ============================================
# Root Agent Definition
# ============================================
# 
# This agent uses the ReAct pattern:
# 1. THOUGHT: Reason about the current situation
# 2. ACTION: Call appropriate tool(s)
# 3. OBSERVATION: Analyze tool results
# 4. Repeat until task is complete
#
# Tools act as "pseudo-agents" - the coordinator decides
# which tool to use based on the current context.
# ============================================

root_agent = Agent(
    # Model configuration
    model=ROOT_AGENT_MODEL,
    
    # Agent identity
    name="lufthansa_travel_buddy",
    description=(
        "Proactive disruption manager for Lufthansa business travelers. "
        "Monitors flights, identifies downstream impacts on meetings and schedules, "
        "finds alternative routing, and drafts professional communications."
    ),
    
    # System instruction (ReAct pattern embedded)
    instruction=ROOT_AGENT_INSTRUCTION,
    
    # Tools available to the agent
    # Organized by domain for clarity
    tools=[
        # --------------------------------
        # Flight Domain Tools (Lufthansa API)
        # --------------------------------
        check_flight_status,        # Get real-time flight status
        find_alternative_flights,   # Find rebooking options
        get_flight_details,         # Get detailed flight info
        get_airport_departures,     # Get departures from airport
        get_airport_arrivals,       # Get arrivals at airport
        
        # --------------------------------
        # Calendar Domain Tools
        # --------------------------------
        get_calendar_events,        # Retrieve calendar events
        find_meeting_conflicts,     # Analyze meeting impacts
        
        # --------------------------------
        # Communication Domain Tools
        # --------------------------------
        draft_delay_notification,   # Draft delay emails
        draft_reschedule_request,   # Draft reschedule requests
        
        # --------------------------------
        # Search Grounding (Built-in)
        # --------------------------------
        google_search,            # Real-time web search for context
        send_email,              # Tool to send emails directly
    ],
)


# ============================================
# Alternative: Multi-Agent Architecture (for v2)
# ============================================
# 
# If you want to use full sub-agents instead of tools,
# uncomment and modify the following:
#
# from google.adk.agents import Agent, AgentTool
# from .sub_agents.flight.agent import flight_agent
# from .sub_agents.calendar.agent import calendar_agent
# from .sub_agents.comms.agent import comms_agent
#
# root_agent = Agent(
#     model="gemini-3-pro-preview",  # Use Pro for complex orchestration
#     name="lufthansa_travel_buddy",
#     instruction=ROOT_AGENT_INSTRUCTION,
#     tools=[
#         AgentTool(agent=flight_agent),
#         AgentTool(agent=calendar_agent),
#         AgentTool(agent=comms_agent),
#         google_search,
#     ],
# )
# ============================================
