"""
Lufthansa Business Travel Buddy - ADK Agent Package

Proactive disruption manager for Lufthansa business travelers.
Built for Hamburg Hackathon: Innovate the Skies & Beyond (Feb 28, 2026)

This package exports `root_agent` which is required by ADK to discover the agent.
"""

from .agent import root_agent

__all__ = ["root_agent"]
