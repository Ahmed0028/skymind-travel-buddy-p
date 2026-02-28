"""
Calendar Domain Tools

Tools for reading calendar events and finding conflicts.
In production, integrate with Google Calendar MCP or Microsoft Graph API.
"""

import logging
from typing import Optional

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


# ============================================
# Mock Calendar Data (for Hackathon Demo)
# ============================================
# TODO: Replace with Google Calendar MCP integration
MOCK_CALENDAR = {
    "2026-02-28": [
        {
            "id": "evt_001",
            "title": "Board Meeting with CEO",
            "start": "16:00",
            "end": "18:00",
            "timezone": "America/New_York",
            "location": "NYC Office - Boardroom",
            "priority": "critical",
            "attendees": [
                {"email": "ceo@company.com", "name": "Jane Smith"},
                {"email": "cfo@company.com", "name": "John Doe"},
            ],
            "description": "Q1 Strategy Review - Presentation Required",
        },
        {
            "id": "evt_002",
            "title": "Client Dinner - Acme Corp",
            "start": "19:00",
            "end": "21:00",
            "timezone": "America/New_York",
            "location": "The Capital Grille, NYC",
            "priority": "important",
            "attendees": [
                {"email": "john@acmecorp.com", "name": "John Client"},
            ],
            "description": "Contract renewal discussion",
        },
        {
            "id": "evt_003",
            "title": "Team Sync Call",
            "start": "10:00",
            "end": "10:30",
            "timezone": "America/New_York",
            "location": "Virtual - Zoom",
            "priority": "flexible",
            "attendees": [
                {"email": "team@company.com", "name": "Dev Team"},
            ],
            "description": "Weekly standup",
        },
    ],
    "2026-03-01": [
        {
            "id": "evt_004",
            "title": "Client Workshop",
            "start": "09:00",
            "end": "12:00",
            "timezone": "America/New_York",
            "location": "Client HQ",
            "priority": "critical",
            "attendees": [
                {"email": "client@bigcorp.com", "name": "Big Corp Team"},
            ],
            "description": "Product demo and training",
        },
    ],
}


def get_calendar_events(
    date: str,
    user_id: str = "default",
    tool_context: ToolContext = None,
) -> dict:
    """
    Retrieve calendar events for a specific date.
    
    Use this tool to see what meetings the user has scheduled
    that might be impacted by flight changes.
    
    Args:
        date: Date in YYYY-MM-DD format (e.g., "2026-02-28")
        user_id: User identifier (optional, for multi-user support)
    
    Returns:
        dict: Calendar information including:
            - date: The requested date
            - event_count: Number of events
            - events: List of events with details
    
    Example:
        >>> get_calendar_events("2026-02-28")
        {
            "date": "2026-02-28",
            "event_count": 3,
            "events": [
                {"title": "Board Meeting", "start": "16:00", ...},
                ...
            ]
        }
    """
    logger.info(f"Getting calendar events for {date}")
    
    # TODO: Replace with Google Calendar MCP call
    # Example with MCP:
    # events = await google_calendar_mcp.list_events(
    #     calendar_id="primary",
    #     time_min=f"{date}T00:00:00Z",
    #     time_max=f"{date}T23:59:59Z",
    # )
    
    events = MOCK_CALENDAR.get(date, [])
    
    result = {
        "date": date,
        "event_count": len(events),
        "events": events,
    }
    
    # Store in context for other tools
    if tool_context:
        tool_context.state["calendar_events"] = events
    
    return result


def find_meeting_conflicts(
    arrival_time: str,
    date: str,
    arrival_timezone: str = "America/New_York",
    user_id: str = "default",
    tool_context: ToolContext = None,
) -> dict:
    """
    Identify meetings that conflict with the new arrival time.
    
    Use this tool after finding alternative flights to see which
    meetings will be impacted by the new schedule. Adds a 1-hour
    buffer after arrival for airport exit and travel.
    
    Args:
        arrival_time: New arrival time in HH:MM format (24-hour)
        date: Date in YYYY-MM-DD format
        arrival_timezone: Timezone of arrival (default: America/New_York)
        user_id: User identifier (optional)
    
    Returns:
        dict: Conflict analysis including:
            - arrival_time: The analyzed arrival time
            - available_from: Earliest meeting time possible (arrival + 1hr buffer)
            - conflicts: List of meetings that will be missed
            - at_risk: List of meetings that may be tight
            - safe: List of meetings that are on track
            - summary: Brief text summary
    
    Example:
        >>> find_meeting_conflicts("18:00", "2026-02-28")
        {
            "conflicts": [{"title": "Board Meeting", "reason": "..."}],
            "safe": [{"title": "Client Dinner", "status": "on_track"}],
            "summary": "1 meeting at risk, 1 on track"
        }
    """
    logger.info(f"Finding conflicts: arrival {arrival_time} on {date}")
    
    events = MOCK_CALENDAR.get(date, [])
    
    # Parse arrival time
    try:
        arrival_hour, arrival_min = map(int, arrival_time.split(":"))
    except ValueError:
        return {"error": f"Invalid arrival_time format: {arrival_time}. Use HH:MM"}
    
    # Add 1 hour buffer for airport exit + travel
    available_hour = arrival_hour + 1
    available_min = arrival_min
    
    conflicts = []
    at_risk = []
    safe = []
    
    for event in events:
        event_start_hour, event_start_min = map(int, event["start"].split(":"))
        
        # Calculate time difference
        event_start_total = event_start_hour * 60 + event_start_min
        available_total = available_hour * 60 + available_min
        
        if available_total > event_start_total:
            # Will miss this meeting
            conflicts.append({
                **event,
                "status": "will_miss",
                "reason": f"Arrives at {arrival_time}, available from {available_hour:02d}:{available_min:02d}, meeting starts at {event['start']}",
            })
        elif available_total > event_start_total - 30:
            # Cutting it close (less than 30 min buffer)
            at_risk.append({
                **event,
                "status": "at_risk",
                "reason": f"Only {event_start_total - available_total} minutes buffer",
            })
        else:
            # Safe
            safe.append({
                **event,
                "status": "on_track",
            })
    
    result = {
        "arrival_time": arrival_time,
        "available_from": f"{available_hour:02d}:{available_min:02d}",
        "conflicts": conflicts,
        "at_risk": at_risk,
        "safe": safe,
        "summary": f"{len(conflicts)} conflict(s), {len(at_risk)} at risk, {len(safe)} on track",
    }
    
    # Store in context
    if tool_context:
        tool_context.state["meeting_conflicts"] = result
    
    return result
