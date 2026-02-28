"""
Lufthansa API Client

Official Lufthansa Open API integration for flight status, schedules, and more.
API Documentation: https://developer.lufthansa.com/docs

Authentication: OAuth 2.0 Client Credentials flow
"""

import logging
import time
from typing import Optional, Dict, Any
import requests

from ..config import (
    LUFTHANSA_CLIENT_ID,
    LUFTHANSA_CLIENT_SECRET,
    LUFTHANSA_API_BASE_URL,
    LUFTHANSA_AUTH_URL,
)

logger = logging.getLogger(__name__)


class LufthansaAPIClient:
    """
    Client for Lufthansa Open API.
    
    Handles OAuth authentication and provides methods for:
    - Flight Status
    - Flight Schedules
    - Reference Data (airports, airlines, aircraft)
    
    Usage:
        client = LufthansaAPIClient()
        status = client.get_flight_status("LH456", "2026-02-28")
    """
    
    def __init__(self):
        self.client_id = LUFTHANSA_CLIENT_ID
        self.client_secret = LUFTHANSA_CLIENT_SECRET
        self.base_url = LUFTHANSA_API_BASE_URL
        self.auth_url = LUFTHANSA_AUTH_URL
        
        # Token cache
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0
    
    def _get_access_token(self) -> str:
        """
        Get OAuth access token, refreshing if expired.
        
        Returns:
            str: Valid access token
        """
        # Check if token is still valid (with 60s buffer)
        if self._access_token and time.time() < self._token_expires_at - 60:
            return self._access_token
        
        logger.info("Refreshing Lufthansa API access token")
        
        try:
            response = requests.post(
                self.auth_url,
                data={
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "grant_type": "client_credentials",
                },
                headers={
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                timeout=10,
            )
            response.raise_for_status()
            
            token_data = response.json()
            self._access_token = token_data["access_token"]
            # Token typically expires in 36000 seconds (10 hours)
            expires_in = token_data.get("expires_in", 36000)
            self._token_expires_at = time.time() + expires_in
            
            logger.info(f"Got new access token, expires in {expires_in}s")
            return self._access_token
            
        except requests.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise RuntimeError(f"Lufthansa API authentication failed: {e}")
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Make authenticated request to Lufthansa API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (without base URL)
            params: Query parameters
        
        Returns:
            dict: JSON response
        """
        token = self._get_access_token()
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                timeout=15,
            )
            response.raise_for_status()
            return response.json()
            
        except requests.HTTPError as e:
            logger.error(f"Lufthansa API error: {e.response.status_code} - {e.response.text}")
            raise
        except requests.RequestException as e:
            logger.error(f"Lufthansa API request failed: {e}")
            raise
    
    # ========================================
    # Flight Status APIs
    # ========================================
    
    def get_flight_status(
        self,
        flight_number: str,
        date: str,
    ) -> Dict[str, Any]:
        """
        Get status of a specific flight.
        
        Args:
            flight_number: IATA flight number (e.g., "LH456")
            date: Flight date in YYYY-MM-DD format
        
        Returns:
            dict: Flight status information including:
                - Departure/arrival times (scheduled, estimated, actual)
                - Terminal and gate information
                - Flight status (scheduled, delayed, cancelled, etc.)
                - Aircraft type
        
        API Endpoint:
            GET /operations/flightstatus/{flightNumber}/{date}
        """
        logger.info(f"Getting flight status: {flight_number} on {date}")
        
        endpoint = f"/operations/flightstatus/{flight_number}/{date}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._parse_flight_status(response)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return {"error": f"Flight {flight_number} not found for {date}"}
            raise
    
    def get_flight_status_by_route(
        self,
        origin: str,
        destination: str,
        date: str,
    ) -> Dict[str, Any]:
        """
        Get status of flights between two airports.
        
        Args:
            origin: Departure airport IATA code (e.g., "HAM")
            destination: Arrival airport IATA code (e.g., "FRA")
            date: Flight date in YYYY-MM-DD format
        
        Returns:
            dict: List of flights on the route with status
        
        API Endpoint:
            GET /operations/flightstatus/route/{origin}/{destination}/{date}
        """
        logger.info(f"Getting flights: {origin} → {destination} on {date}")
        
        endpoint = f"/operations/flightstatus/route/{origin}/{destination}/{date}"
        
        try:
            response = self._make_request("GET", endpoint)
            return self._parse_route_flights(response)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return {"flights": [], "message": f"No flights found {origin}→{destination} on {date}"}
            raise
    
    def get_arrivals(
        self,
        airport: str,
        from_time: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Get arriving flights at an airport.
        
        Args:
            airport: Airport IATA code (e.g., "FRA")
            from_time: Start time in ISO format (YYYY-MM-DDTHH:MM)
            limit: Maximum number of flights to return
        
        API Endpoint:
            GET /operations/flightstatus/arrivals/{airport}/{fromDateTime}
        """
        endpoint = f"/operations/flightstatus/arrivals/{airport}/{from_time}"
        return self._make_request("GET", endpoint, {"limit": limit})
    
    def get_departures(
        self,
        airport: str,
        from_time: str,
        limit: int = 20,
    ) -> Dict[str, Any]:
        """
        Get departing flights from an airport.
        
        Args:
            airport: Airport IATA code (e.g., "HAM")
            from_time: Start time in ISO format (YYYY-MM-DDTHH:MM)
            limit: Maximum number of flights to return
        
        API Endpoint:
            GET /operations/flightstatus/departures/{airport}/{fromDateTime}
        """
        endpoint = f"/operations/flightstatus/departures/{airport}/{from_time}"
        return self._make_request("GET", endpoint, {"limit": limit})
    
    # ========================================
    # Flight Schedules APIs
    # ========================================
    
    def get_schedules(
        self,
        origin: str,
        destination: str,
        date: str,
        direct_flights: bool = False,
    ) -> Dict[str, Any]:
        """
        Get scheduled flights between two airports.
        
        Args:
            origin: Departure airport IATA code
            destination: Arrival airport IATA code
            date: Flight date in YYYY-MM-DD format
            direct_flights: If True, only return non-stop flights
        
        API Endpoint:
            GET /operations/schedules/{origin}/{destination}/{fromDateTime}
        """
        logger.info(f"Getting schedules: {origin} → {destination} on {date}")
        
        endpoint = f"/operations/schedules/{origin}/{destination}/{date}"
        params = {"directFlights": direct_flights}
        
        try:
            return self._make_request("GET", endpoint, params)
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                return {"schedules": [], "message": "No schedules found"}
            raise
    
    # ========================================
    # Reference Data APIs
    # ========================================
    
    def get_airport(self, airport_code: str) -> Dict[str, Any]:
        """Get airport information by IATA code."""
        endpoint = f"/references/airports/{airport_code}"
        return self._make_request("GET", endpoint)
    
    def get_airline(self, airline_code: str) -> Dict[str, Any]:
        """Get airline information by IATA code."""
        endpoint = f"/references/airlines/{airline_code}"
        return self._make_request("GET", endpoint)
    
    def get_aircraft(self, aircraft_code: str) -> Dict[str, Any]:
        """Get aircraft information by IATA code."""
        endpoint = f"/references/aircraft/{aircraft_code}"
        return self._make_request("GET", endpoint)
    
    # ========================================
    # Response Parsers
    # ========================================
    
    def _parse_flight_status(self, response: Dict) -> Dict[str, Any]:
        """Parse flight status response into clean format."""
        try:
            flight_data = response.get("FlightStatusResource", {})
            flights = flight_data.get("Flights", {}).get("Flight", [])
            
            if not flights:
                return {"error": "No flight data in response"}
            
            # Handle single flight vs list
            flight = flights[0] if isinstance(flights, list) else flights
            
            departure = flight.get("Departure", {})
            arrival = flight.get("Arrival", {})
            status = flight.get("FlightStatus", {})
            equipment = flight.get("Equipment", {})
            
            return {
                "flight": flight.get("MarketingCarrier", {}).get("FlightNumber", ""),
                "airline": flight.get("MarketingCarrier", {}).get("AirlineID", ""),
                "status": status.get("Code", "unknown"),
                "status_description": self._get_status_description(status.get("Code", "")),
                "departure": {
                    "airport": departure.get("AirportCode", ""),
                    "terminal": departure.get("Terminal", {}).get("Name", ""),
                    "gate": departure.get("Terminal", {}).get("Gate", ""),
                    "scheduled": departure.get("ScheduledTimeLocal", {}).get("DateTime", ""),
                    "estimated": departure.get("EstimatedTimeLocal", {}).get("DateTime", ""),
                    "actual": departure.get("ActualTimeLocal", {}).get("DateTime", ""),
                },
                "arrival": {
                    "airport": arrival.get("AirportCode", ""),
                    "terminal": arrival.get("Terminal", {}).get("Name", ""),
                    "gate": arrival.get("Terminal", {}).get("Gate", ""),
                    "scheduled": arrival.get("ScheduledTimeLocal", {}).get("DateTime", ""),
                    "estimated": arrival.get("EstimatedTimeLocal", {}).get("DateTime", ""),
                    "actual": arrival.get("ActualTimeLocal", {}).get("DateTime", ""),
                },
                "aircraft": {
                    "code": equipment.get("AircraftCode", ""),
                    "registration": equipment.get("AircraftRegistration", ""),
                },
            }
            
        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing flight status: {e}")
            return {"error": f"Failed to parse flight status: {e}", "raw": response}
    
    def _parse_route_flights(self, response: Dict) -> Dict[str, Any]:
        """Parse route flights response."""
        try:
            flight_data = response.get("FlightStatusResource", {})
            flights = flight_data.get("Flights", {}).get("Flight", [])
            
            if not isinstance(flights, list):
                flights = [flights] if flights else []
            
            parsed_flights = []
            for flight in flights:
                parsed_flights.append(self._parse_single_flight(flight))
            
            return {"flights": parsed_flights, "count": len(parsed_flights)}
            
        except (KeyError, TypeError) as e:
            logger.error(f"Error parsing route flights: {e}")
            return {"flights": [], "error": str(e)}
    
    def _parse_single_flight(self, flight: Dict) -> Dict[str, Any]:
        """Parse a single flight from the response."""
        departure = flight.get("Departure", {})
        arrival = flight.get("Arrival", {})
        
        return {
            "flight": f"{flight.get('MarketingCarrier', {}).get('AirlineID', '')}{flight.get('MarketingCarrier', {}).get('FlightNumber', '')}",
            "status": flight.get("FlightStatus", {}).get("Code", ""),
            "departure_time": departure.get("ScheduledTimeLocal", {}).get("DateTime", ""),
            "arrival_time": arrival.get("ScheduledTimeLocal", {}).get("DateTime", ""),
            "origin": departure.get("AirportCode", ""),
            "destination": arrival.get("AirportCode", ""),
        }
    
    def _get_status_description(self, code: str) -> str:
        """Convert status code to human-readable description."""
        status_map = {
            "CD": "Cancelled",
            "DP": "Departed",
            "LD": "Landed",
            "RT": "Rerouted",
            "DV": "Diverted",
            "HD": "On Hold",
            "FE": "Flight Early",
            "NI": "Next Information",
            "OT": "On Time",
            "DL": "Delayed",
            "NO": "No Status",
        }
        return status_map.get(code, f"Unknown ({code})")


# Create singleton instance
lufthansa_client = LufthansaAPIClient()
