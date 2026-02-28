"""
Flight Domain Tools

Tools for checking flight status, finding alternatives, and getting details.
Uses the official Lufthansa Open API for authentic data.
"""

import logging
from typing import Optional
from datetime import datetime, timedelta

from google.adk.tools import ToolContext

from ...tools.lufthansa_api import lufthansa_client
from ...config import LUFTHANSA_GROUP_AIRLINES

logger = logging.getLogger(__name__)


def check_flight_status(
    flight_number: str = None,
    date: str = None,
    booking_id: str = None,
    tool_context: ToolContext = None,
) -> dict:
    """
    Check the current status of a Lufthansa flight.
    
    Use this tool to get real-time delay and cancellation information
    for a specific flight using the official Lufthansa API.
    
    Args:
        flight_number: IATA flight number (e.g., "LH456", "LH 456", "456")
                       Will auto-prefix "LH" if just a number is provided.
        date: Flight date in YYYY-MM-DD format. Defaults to today.
        booking_id: Lufthansa booking reference (e.g., "ABC123"). 
                    Note: Booking lookup requires additional API access.
    
    Returns:
        dict: Flight status including:
            - flight: IATA flight number
            - airline: Airline code
            - status: Current status code
            - status_description: Human-readable status
            - departure: Departure details (airport, times, gate, terminal)
            - arrival: Arrival details (airport, times)
            - aircraft: Aircraft information
    
    Example:
        >>> check_flight_status(flight_number="LH456", date="2026-02-28")
        {
            "flight": "456",
            "airline": "LH",
            "status": "DL",
            "status_description": "Delayed",
            "departure": {"airport": "HAM", "scheduled": "10:00", ...}
        }
    """
    logger.info(f"Checking flight status: {flight_number} on {date}")
    
    # Default to today if no date provided
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Handle booking ID (would need Lufthansa booking API)
    if booking_id and not flight_number:
        return {
            "error": "Booking ID lookup requires Lufthansa Partner API access. Please provide the flight number directly.",
            "hint": "You can find your flight number on your booking confirmation email."
        }
    
    if not flight_number:
        return {"error": "Please provide a flight_number (e.g., 'LH456')"}
    
    # Normalize flight number
    flight_number = flight_number.upper().replace(" ", "")
    
    # Add LH prefix if just a number
    if flight_number.isdigit():
        flight_number = f"LH{flight_number}"
    
    try:
        result = lufthansa_client.get_flight_status(flight_number, date)
        
        # Store in context for other tools to use
        if tool_context and "error" not in result:
            tool_context.state["current_flight"] = result
            tool_context.state["flight_number"] = flight_number
            tool_context.state["flight_date"] = date
        
        return result
        
    except Exception as e:
        logger.error(f"Error fetching flight status: {e}")
        return {"error": f"Failed to fetch flight status: {str(e)}"}


def find_alternative_flights(
    origin: str,
    destination: str,
    date: str = None,
    preferred_class: str = "business",
    direct_only: bool = False,
    tool_context: ToolContext = None,
) -> dict:
    """
    Find alternative Lufthansa Group flights for rebooking.
    
    Use this tool when a flight is delayed or cancelled and the user
    needs alternative routing options. Searches official Lufthansa schedules.
    
    Args:
        origin: Departure airport IATA code (e.g., "HAM", "FRA", "MUC")
        destination: Arrival airport IATA code (e.g., "JFK", "LHR", "CDG")
        date: Travel date in YYYY-MM-DD format. Defaults to today.
        preferred_class: Cabin class preference ("business" or "economy")
        direct_only: If True, only return non-stop flights
    
    Returns:
        dict: Alternative flights including:
            - flights: List of alternative flights with times and status
            - count: Number of alternatives found
            - recommendation: Suggested best option
    
    Example:
        >>> find_alternative_flights("HAM", "JFK", "2026-02-28")
        {
            "flights": [
                {"flight": "LH2042", "departure_time": "10:30", ...},
            ],
            "count": 3,
            "recommendation": "LH2042 - earliest arrival"
        }
    """
    logger.info(f"Finding alternatives: {origin} → {destination} on {date}")
    
    # Default to today
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Normalize airport codes
    origin = origin.upper().strip()
    destination = destination.upper().strip()
    
    try:
        # Get flights on the route
        result = lufthansa_client.get_flight_status_by_route(origin, destination, date)
        
        flights = result.get("flights", [])
        
        # Filter for Lufthansa Group if needed
        lh_flights = [
            f for f in flights 
            if any(f.get("flight", "").startswith(code) for code in LUFTHANSA_GROUP_AIRLINES)
        ]
        
        # Sort by departure time
        lh_flights.sort(key=lambda f: f.get("departure_time", ""))
        
        # Add recommendation
        recommendation = None
        if lh_flights:
            # Find first non-cancelled flight
            for flight in lh_flights:
                if flight.get("status") != "CD":  # Not cancelled
                    recommendation = f"{flight['flight']} - departs {flight.get('departure_time', 'N/A')}"
                    break
        
        result = {
            "origin": origin,
            "destination": destination,
            "date": date,
            "flights": lh_flights[:5],  # Top 5
            "count": len(lh_flights),
            "recommendation": recommendation,
            "preferred_class": preferred_class,
        }
        
        # Store in context
        if tool_context:
            tool_context.state["alternatives"] = result
        
        return result
        
    except Exception as e:
        logger.error(f"Error finding alternatives: {e}")
        return {"error": f"Failed to find alternatives: {str(e)}"}


def get_flight_details(
    flight_number: str,
    date: str = None,
    tool_context: ToolContext = None,
) -> dict:
    """
    Get detailed information about a specific Lufthansa flight.
    
    Use this tool when you need comprehensive flight details
    including aircraft type, route info, and current status.
    
    Args:
        flight_number: IATA flight number (e.g., "LH456")
        date: Flight date in YYYY-MM-DD format. Defaults to today.
    
    Returns:
        dict: Detailed flight information including:
            - Full departure/arrival details with terminals and gates
            - Aircraft type and registration
            - Current flight status
            - Scheduled vs actual times
    """
    logger.info(f"Getting flight details: {flight_number}")
    
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    
    # Normalize flight number
    flight_number = flight_number.upper().replace(" ", "")
    if flight_number.isdigit():
        flight_number = f"LH{flight_number}"
    
    try:
        return lufthansa_client.get_flight_status(flight_number, date)
    except Exception as e:
        logger.error(f"Error getting flight details: {e}")
        return {"error": f"Failed to get flight details: {str(e)}"}


def get_airport_departures(
    airport: str,
    from_time: str = None,
    limit: int = 10,
    tool_context: ToolContext = None,
) -> dict:
    """
    Get upcoming departures from an airport.
    
    Use this tool to see all Lufthansa departures from a specific airport,
    useful for finding alternative flights or checking overall operations.
    
    Args:
        airport: Airport IATA code (e.g., "HAM", "FRA")
        from_time: Start time in YYYY-MM-DDTHH:MM format. Defaults to now.
        limit: Maximum flights to return (default 10)
    
    Returns:
        dict: List of departing flights with status
    """
    logger.info(f"Getting departures from {airport}")
    
    airport = airport.upper().strip()
    
    if not from_time:
        from_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    try:
        return lufthansa_client.get_departures(airport, from_time, limit)
    except Exception as e:
        logger.error(f"Error getting departures: {e}")
        return {"error": f"Failed to get departures: {str(e)}"}


def get_airport_arrivals(
    airport: str,
    from_time: str = None,
    limit: int = 10,
    tool_context: ToolContext = None,
) -> dict:
    """
    Get upcoming arrivals at an airport.
    
    Use this tool to check arrival status at the destination airport,
    useful for understanding if delays are affecting all flights.
    
    Args:
        airport: Airport IATA code (e.g., "JFK", "LHR")
        from_time: Start time in YYYY-MM-DDTHH:MM format. Defaults to now.
        limit: Maximum flights to return (default 10)
    
    Returns:
        dict: List of arriving flights with status
    """
    logger.info(f"Getting arrivals at {airport}")
    
    airport = airport.upper().strip()
    
    if not from_time:
        from_time = datetime.now().strftime("%Y-%m-%dT%H:%M")
    
    try:
        return lufthansa_client.get_arrivals(airport, from_time, limit)
    except Exception as e:
        logger.error(f"Error getting arrivals: {e}")
        return {"error": f"Failed to get arrivals: {str(e)}"}
