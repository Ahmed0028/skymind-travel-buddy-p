"""
Communications Domain Tools

Tools for drafting professional notifications and reschedule requests.
Uses templates for consistent, professional business communication.
"""

import logging
from typing import Optional, List

from google.adk.tools import ToolContext

logger = logging.getLogger(__name__)


def draft_delay_notification(
    recipient_email: str,
    recipient_name: str,
    delay_info: str,
    new_arrival: str,
    meeting_impact: str = None,
    sender_name: str = "Traveler",
    tool_context: ToolContext = None,
) -> dict:
    """
    Draft a professional delay notification email.
    
    Use this tool to create ready-to-send emails notifying
    colleagues, clients, or family about flight delays.
    Generates professional, concise business communication.
    
    Args:
        recipient_email: Email address of recipient
        recipient_name: Name of recipient for personalization
        delay_info: Description of the delay (e.g., "90 minute delay due to weather")
        new_arrival: New expected arrival time (e.g., "18:00 EST")
        meeting_impact: Optional description of meeting impact
        sender_name: Name of the sender (optional)
    
    Returns:
        dict: Email draft with:
            - type: "email"
            - to: Recipient email
            - subject: Email subject line
            - body: Email body text
            - status: "draft"
    
    Example:
        >>> draft_delay_notification(
        ...     recipient_email="ceo@company.com",
        ...     recipient_name="Jane",
        ...     delay_info="90 minute delay due to weather in Frankfurt",
        ...     new_arrival="18:00 EST",
        ...     meeting_impact="I will arrive 30 minutes before our board meeting"
        ... )
    """
    logger.info(f"Drafting delay notification to {recipient_email}")
    
    subject = f"Travel Update: Flight Delay - New Arrival {new_arrival}"
    
    # Build email body
    body_parts = [
        f"Dear {recipient_name},",
        "",
        "I wanted to inform you that my flight has experienced a delay. Here are the updated details:",
        "",
        f"**Delay:** {delay_info}",
        f"**New Arrival:** {new_arrival}",
    ]
    
    if meeting_impact:
        body_parts.extend([
            "",
            f"**Impact on Our Meeting:** {meeting_impact}",
        ])
    
    body_parts.extend([
        "",
        "I will keep you updated if there are any further changes. Please let me know if we need to adjust our plans.",
        "",
        "Best regards,",
        sender_name,
    ])
    
    body = "\n".join(body_parts)
    
    result = {
        "type": "email",
        "to": recipient_email,
        "subject": subject,
        "body": body,
        "status": "draft",
    }
    
    # Store in context
    if tool_context:
        drafts = tool_context.state.get("email_drafts", [])
        drafts.append(result)
        tool_context.state["email_drafts"] = drafts
    
    return result


def draft_reschedule_request(
    recipient_email: str,
    recipient_name: str,
    original_time: str,
    proposed_times: List[str],
    reason: str,
    meeting_title: str = None,
    sender_name: str = "Traveler",
    tool_context: ToolContext = None,
) -> dict:
    """
    Draft a meeting reschedule request email.
    
    Use this tool to propose new meeting times when the original
    time is no longer feasible due to travel changes.
    
    Args:
        recipient_email: Email address of recipient
        recipient_name: Name of recipient
        original_time: Original meeting time (e.g., "16:00 EST")
        proposed_times: List of proposed alternative times
        reason: Brief reason for reschedule (e.g., "flight delay")
        meeting_title: Optional title of the meeting
        sender_name: Name of the sender (optional)
    
    Returns:
        dict: Email draft with subject, body, and proposed times
    
    Example:
        >>> draft_reschedule_request(
        ...     recipient_email="client@acme.com",
        ...     recipient_name="John",
        ...     original_time="16:00 EST",
        ...     proposed_times=["17:00 EST", "18:00 EST", "Tomorrow 09:00 EST"],
        ...     reason="flight delay from Frankfurt"
        ... )
    """
    logger.info(f"Drafting reschedule request to {recipient_email}")
    
    meeting_ref = f" ({meeting_title})" if meeting_title else ""
    subject = f"Meeting Reschedule Request: {original_time}{meeting_ref}"
    
    # Format proposed times as a list
    times_formatted = "\n".join([f"  • {t}" for t in proposed_times])
    
    body_parts = [
        f"Dear {recipient_name},",
        "",
        f"Due to {reason}, I need to request a reschedule of our meeting originally planned for {original_time}{meeting_ref}.",
        "",
        "Would any of the following alternative times work for you?",
        "",
        times_formatted,
        "",
        "I apologize for any inconvenience and appreciate your flexibility.",
        "",
        "Best regards,",
        sender_name,
    ]
    
    body = "\n".join(body_parts)
    
    result = {
        "type": "email",
        "to": recipient_email,
        "subject": subject,
        "body": body,
        "proposed_times": proposed_times,
        "original_time": original_time,
        "status": "draft",
    }
    
    # Store in context
    if tool_context:
        drafts = tool_context.state.get("email_drafts", [])
        drafts.append(result)
        tool_context.state["email_drafts"] = drafts
    
    return result
def send_email(
    to_email: str,
    subject: str,
    body: str,
) -> dict:
    """
    Send an email to the specified recipient.
    
    Args:
        to_email: Recipient email address
        subject: Email subject line
        body: Email body content
        
    Returns:
        Confirmation of email sent
    """
    # For demo - just simulate sending
    # In production, integrate with Gmail API or SMTP
    
    print(f"\n📧 SENDING EMAIL:")
    print(f"   To: {to_email}")
    print(f"   Subject: {subject}")
    print(f"   Body: {body[:100]}...")
    
    return {
        "status": "sent",
        "to": to_email,
        "subject": subject,
        "message": f"Email successfully sent to {to_email}"
    }