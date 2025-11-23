"""Google Calendar MCP Server"""
import asyncio
from datetime import datetime, timedelta
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from .auth import get_calendar_service, get_gmail_service
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os

app = Server("google-calendar-mcp")

def format_datetime(dt_str: str) -> str:
    """Format ISO datetime to readable string"""
    try:
        dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        return dt.strftime('%a, %b %d at %I:%M %p')
    except:
        return dt_str

def parse_datetime_input(date_str: str, time_str: str = None) -> str:
    """Parse user input into ISO datetime"""
    # Simple parsing - can be enhanced
    from dateutil import parser
    if time_str:
        dt = parser.parse(f"{date_str} {time_str}")
    else:
        dt = parser.parse(date_str)
    return dt.isoformat()

@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available calendar tools"""
    return [
        Tool(
            name="list_events",
            description="List calendar events for a time range",
            inputSchema={
                "type": "object",
                "properties": {
                    "time_range": {
                        "type": "string",
                        "description": "Time range: 'today', 'tomorrow', 'this_week', 'next_week', or 'custom'",
                        "enum": ["today", "tomorrow", "this_week", "next_week", "custom"]
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of events to return (default: 10)",
                        "default": 10
                    },
                    "start_date": {
                        "type": "string",
                        "description": "Start date for custom range (ISO format or natural language)"
                    },
                    "end_date": {
                        "type": "string",
                        "description": "End date for custom range (ISO format or natural language)"
                    }
                },
                "required": ["time_range"]
            }
        ),
        Tool(
            name="create_event",
            description="Create a new calendar event",
            inputSchema={
                "type": "object",
                "properties": {
                    "summary": {
                        "type": "string",
                        "description": "Event title/summary"
                    },
                    "start_time": {
                        "type": "string",
                        "description": "Start time (ISO format or natural language like '2024-11-25 2:00 PM')"
                    },
                    "end_time": {
                        "type": "string",
                        "description": "End time (ISO format or natural language)"
                    },
                    "description": {
                        "type": "string",
                        "description": "Event description (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Event location (optional)"
                    },
                    "attendees": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of attendee email addresses (optional)"
                    },
                    "send_invites": {
                        "type": "boolean",
                        "description": "Whether to send email invitations to attendees (default: false)",
                        "default": False
                    }
                },
                "required": ["summary", "start_time", "end_time"]
            }
        ),
        Tool(
            name="delete_event",
            description="Delete a calendar event by ID",
            inputSchema={
                "type": "object",
                "properties": {
                    "event_id": {
                        "type": "string",
                        "description": "Event ID to delete"
                    },
                    "send_invites": {
                        "type": "boolean",
                        "description": "Whether to send email invitations to attendees (default: false)",
                        "default": False
                    }
                },
                "required": ["event_id"]
            }
        ),
        Tool(
            name="find_free_slots",
            description="Find available time slots in calendar",
            inputSchema={
                "type": "object",
                "properties": {
                    "duration_minutes": {
                        "type": "number",
                        "description": "Duration needed in minutes (default: 60)",
                        "default": 60
                    },
                    "days_ahead": {
                        "type": "number",
                        "description": "How many days ahead to search (default: 7)",
                        "default": 7
                    },
                    "work_hours_only": {
                        "type": "boolean",
                        "description": "Only show slots during work hours 9 AM - 5 PM (default: true)",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="search_events",
            description="Search for events by keyword",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (searches in title, description, location)"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum results to return (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="send_email",
            description="Send an email via Gmail",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body (plain text or HTML)"
                    },
                    "html": {
                        "type": "boolean",
                        "description": "Whether body is HTML (default: false)",
                        "default": False
                    },
                    "cc": {
                        "type": "string",
                        "description": "CC email addresses (comma-separated, optional)"
                    },
                    "bcc": {
                        "type": "string",
                        "description": "BCC email addresses (comma-separated, optional)"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="list_emails",
            description="List emails from inbox, sent, or other folders",
            inputSchema={
                "type": "object",
                "properties": {
                    "folder": {
                        "type": "string",
                        "description": "Folder to list: 'inbox', 'sent', 'drafts', 'all' (default: inbox)",
                        "default": "inbox"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum number of emails to return (default: 10)",
                        "default": 10
                    },
                    "unread_only": {
                        "type": "boolean",
                        "description": "Only show unread emails (default: false)",
                        "default": False
                    }
                }
            }
        ),
        Tool(
            name="search_emails",
            description="Search emails by query",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query (e.g., 'from:user@example.com', 'subject:meeting', 'after:2024/01/01')"
                    },
                    "max_results": {
                        "type": "number",
                        "description": "Maximum results (default: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="read_email",
            description="Read full content of a specific email",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email message ID"
                    }
                },
                "required": ["email_id"]
            }
        ),
        Tool(
            name="mark_email",
            description="Mark email as read/unread",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email message ID"
                    },
                    "mark_as": {
                        "type": "string",
                        "description": "Action: 'read' or 'unread'",
                        "enum": ["read", "unread"]
                    }
                },
                "required": ["email_id", "mark_as"]
            }
        ),
        Tool(
            name="delete_email",
            description="Delete or trash an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email message ID"
                    },
                    "permanent": {
                        "type": "boolean",
                        "description": "Permanently delete (true) or move to trash (false, default)",
                        "default": False
                    }
                },
                "required": ["email_id"]
            }
        ),
        Tool(
            name="reply_to_email",
            description="Reply to an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email message ID to reply to"
                    },
                    "body": {
                        "type": "string",
                        "description": "Reply message body"
                    }
                },
                "required": ["email_id", "body"]
            }
        ),
        Tool(
            name="create_draft",
            description="Create an email draft",
            inputSchema={
                "type": "object",
                "properties": {
                    "to": {
                        "type": "string",
                        "description": "Recipient email address"
                    },
                    "subject": {
                        "type": "string",
                        "description": "Email subject"
                    },
                    "body": {
                        "type": "string",
                        "description": "Email body"
                    }
                },
                "required": ["to", "subject", "body"]
            }
        ),
        Tool(
            name="list_labels",
            description="List all Gmail labels/folders",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="add_label",
            description="Add label to an email",
            inputSchema={
                "type": "object",
                "properties": {
                    "email_id": {
                        "type": "string",
                        "description": "Email message ID"
                    },
                    "label": {
                        "type": "string",
                        "description": "Label name to add"
                    }
                },
                "required": ["email_id", "label"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
        # Gmail tools
        gmail_tools = ["send_email", "list_emails", "search_emails", "read_email", 
                       "mark_email", "delete_email", "reply_to_email", "create_draft",
                       "list_labels", "add_label"]
        
        if name in gmail_tools:
            gmail_service = get_gmail_service()
            
            if name == "send_email":
                return await handle_send_email(gmail_service, arguments)
            elif name == "list_emails":
                return await handle_list_emails(gmail_service, arguments)
            elif name == "search_emails":
                return await handle_search_emails(gmail_service, arguments)
            elif name == "read_email":
                return await handle_read_email(gmail_service, arguments)
            elif name == "mark_email":
                return await handle_mark_email(gmail_service, arguments)
            elif name == "delete_email":
                return await handle_delete_email(gmail_service, arguments)
            elif name == "reply_to_email":
                return await handle_reply_to_email(gmail_service, arguments)
            elif name == "create_draft":
                return await handle_create_draft(gmail_service, arguments)
            elif name == "list_labels":
                return await handle_list_labels(gmail_service, arguments)
            elif name == "add_label":
                return await handle_add_label(gmail_service, arguments)
        else:
            # Calendar tools
            service = get_calendar_service()
            
            if name == "list_events":
                return await handle_list_events(service, arguments)
            elif name == "create_event":
                return await handle_create_event(service, arguments)
            elif name == "delete_event":
                return await handle_delete_event(service, arguments)
            elif name == "find_free_slots":
                return await handle_find_free_slots(service, arguments)
            elif name == "search_events":
                return await handle_search_events(service, arguments)
            else:
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
    
    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]

async def handle_list_events(service, args):
    """List calendar events"""
    time_range = args.get("time_range", "today")
    max_results = args.get("max_results", 10)
    
    now = datetime.utcnow()
    
    # Calculate time range
    if time_range == "today":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif time_range == "tomorrow":
        start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
    elif time_range == "this_week":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    elif time_range == "next_week":
        start = (now + timedelta(days=7)).replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
    else:  # custom
        from dateutil import parser
        start = parser.parse(args.get("start_date", now.isoformat()))
        end = parser.parse(args.get("end_date", (now + timedelta(days=7)).isoformat()))
    
    # Fetch events
    events_result = service.events().list(
        calendarId='primary',
        timeMin=start.isoformat() + 'Z',
        timeMax=end.isoformat() + 'Z',
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        return [TextContent(type="text", text=f"No events found for {time_range}")]
    
    # Format output
    output = f"📅 Events for {time_range}:\n\n"
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        location = event.get('location', '')
        event_id = event['id']
        
        output += f"• {format_datetime(start_time)}\n"
        output += f"  {summary}\n"
        if location:
            output += f"  📍 {location}\n"
        output += f"  ID: {event_id}\n\n"
    
    return [TextContent(type="text", text=output)]

async def handle_create_event(service, args):
    """Create a new calendar event"""
    from dateutil import parser
    
    summary = args["summary"]
    start_time = parser.parse(args["start_time"])
    end_time = parser.parse(args["end_time"])
    
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_time.isoformat(),
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time.isoformat(),
            'timeZone': 'UTC',
        },
    }
    
    if 'description' in args:
        event['description'] = args['description']
    if 'location' in args:
        event['location'] = args['location']
    if 'attendees' in args:
        event['attendees'] = [{'email': email} for email in args['attendees']]
    
    # Only send email invites if explicitly requested
    send_updates = 'all' if args.get('send_invites', False) else 'none'
    created_event = service.events().insert(calendarId='primary', body=event, sendUpdates=send_updates).execute()
    
    output = f"✅ Event created successfully!\n\n"
    output += f"📅 {summary}\n"
    output += f"🕐 {format_datetime(start_time.isoformat())}\n"
    output += f"ID: {created_event['id']}\n"
    output += f"Link: {created_event.get('htmlLink', 'N/A')}"
    
    return [TextContent(type="text", text=output)]

async def handle_delete_event(service, args):
    """Delete a calendar event"""
    event_id = args["event_id"]
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return [TextContent(type="text", text=f"✅ Event {event_id} deleted successfully")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to delete event: {str(e)}")]

async def handle_find_free_slots(service, args):
    """Find free time slots"""
    duration = args.get("duration_minutes", 60)
    days_ahead = args.get("days_ahead", 7)
    work_hours_only = args.get("work_hours_only", True)
    
    now = datetime.utcnow()
    end_date = now + timedelta(days=days_ahead)
    
    # Fetch all events in range
    events_result = service.events().list(
        calendarId='primary',
        timeMin=now.isoformat() + 'Z',
        timeMax=end_date.isoformat() + 'Z',
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    # Find gaps between events
    free_slots = []
    current_time = now
    
    for event in events:
        event_start = datetime.fromisoformat(event['start'].get('dateTime', event['start'].get('date')).replace('Z', '+00:00'))
        
        # Check if there's a gap
        gap_minutes = (event_start - current_time).total_seconds() / 60
        if gap_minutes >= duration:
            if not work_hours_only or (9 <= current_time.hour < 17):
                free_slots.append({
                    'start': current_time,
                    'end': event_start,
                    'duration': gap_minutes
                })
        
        event_end = datetime.fromisoformat(event['end'].get('dateTime', event['end'].get('date')).replace('Z', '+00:00'))
        current_time = max(current_time, event_end)
    
    # Format output
    if not free_slots:
        return [TextContent(type="text", text=f"No free slots found for {duration} minutes in the next {days_ahead} days")]
    
    output = f"🕐 Available {duration}-minute slots:\n\n"
    for slot in free_slots[:10]:  # Limit to 10 slots
        output += f"• {format_datetime(slot['start'].isoformat())}\n"
        output += f"  Duration: {int(slot['duration'])} minutes\n\n"
    
    return [TextContent(type="text", text=output)]

async def handle_search_events(service, args):
    """Search for events"""
    query = args["query"]
    max_results = args.get("max_results", 10)
    
    events_result = service.events().list(
        calendarId='primary',
        q=query,
        maxResults=max_results,
        singleEvents=True,
        orderBy='startTime'
    ).execute()
    
    events = events_result.get('items', [])
    
    if not events:
        return [TextContent(type="text", text=f"No events found matching '{query}'")]
    
    output = f"🔍 Search results for '{query}':\n\n"
    for event in events:
        start_time = event['start'].get('dateTime', event['start'].get('date'))
        summary = event.get('summary', 'No title')
        output += f"• {format_datetime(start_time)} - {summary}\n"
        output += f"  ID: {event['id']}\n\n"
    
    return [TextContent(type="text", text=output)]

async def handle_send_email(service, args):
    """Send an email via Gmail"""
    to = args["to"]
    subject = args["subject"]
    body = args["body"]
    is_html = args.get("html", False)
    
    # Create message
    if is_html:
        message = MIMEText(body, 'html')
    else:
        message = MIMEText(body)
    
    message['to'] = to
    message['subject'] = subject
    
    if 'cc' in args:
        message['cc'] = args['cc']
    if 'bcc' in args:
        message['bcc'] = args['bcc']
    
    # Encode message
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
    
    try:
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        output = f"✅ Email sent successfully!\n\n"
        output += f"📧 To: {to}\n"
        output += f"📝 Subject: {subject}\n"
        output += f"Message ID: {sent_message['id']}"
        
        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to send email: {str(e)}")]

async def handle_list_emails(service, args):
    """List emails from specified folder"""
    folder = args.get("folder", "inbox")
    max_results = args.get("max_results", 10)
    unread_only = args.get("unread_only", False)
    
    # Build query
    query_parts = []
    if folder == "inbox":
        query_parts.append("in:inbox")
    elif folder == "sent":
        query_parts.append("in:sent")
    elif folder == "drafts":
        query_parts.append("in:drafts")
    
    if unread_only:
        query_parts.append("is:unread")
    
    query = " ".join(query_parts) if query_parts else None
    
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return [TextContent(type="text", text=f"No emails found in {folder}")]
        
        output = f"📬 Emails in {folder}:\n\n"
        
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
            
            output += f"• From: {headers.get('From', 'Unknown')}\n"
            output += f"  Subject: {headers.get('Subject', 'No subject')}\n"
            output += f"  Date: {headers.get('Date', 'Unknown')}\n"
            output += f"  ID: {msg['id']}\n\n"
        
        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to list emails: {str(e)}")]

async def handle_search_emails(service, args):
    """Search emails by query"""
    query = args["query"]
    max_results = args.get("max_results", 10)
    
    try:
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            return [TextContent(type="text", text=f"No emails found matching '{query}'")]
        
        output = f"🔍 Search results for '{query}':\n\n"
        
        for msg in messages:
            msg_data = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            headers = {h['name']: h['value'] for h in msg_data['payload']['headers']}
            
            output += f"• From: {headers.get('From', 'Unknown')}\n"
            output += f"  Subject: {headers.get('Subject', 'No subject')}\n"
            output += f"  Date: {headers.get('Date', 'Unknown')}\n"
            output += f"  ID: {msg['id']}\n\n"
        
        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to search emails: {str(e)}")]

async def handle_read_email(service, args):
    """Read full email content"""
    email_id = args["email_id"]
    
    try:
        msg = service.users().messages().get(
            userId='me',
            id=email_id,
            format='full'
        ).execute()
        
        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        
        # Extract body
        body = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            body = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        
        output = f"📧 Email Details:\n\n"
        output += f"From: {headers.get('From', 'Unknown')}\n"
        output += f"To: {headers.get('To', 'Unknown')}\n"
        output += f"Subject: {headers.get('Subject', 'No subject')}\n"
        output += f"Date: {headers.get('Date', 'Unknown')}\n\n"
        output += f"Body:\n{body[:1000]}"  # Limit body to 1000 chars
        
        if len(body) > 1000:
            output += "\n\n[... truncated]"
        
        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to read email: {str(e)}")]

async def handle_mark_email(service, args):
    """Mark email as read/unread"""
    email_id = args["email_id"]
    mark_as = args["mark_as"]
    
    try:
        if mark_as == "read":
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return [TextContent(type="text", text=f"✅ Email marked as read")]
        else:
            service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': ['UNREAD']}
            ).execute()
            return [TextContent(type="text", text=f"✅ Email marked as unread")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to mark email: {str(e)}")]

async def handle_delete_email(service, args):
    """Delete or trash email"""
    email_id = args["email_id"]
    permanent = args.get("permanent", False)
    
    try:
        if permanent:
            service.users().messages().delete(userId='me', id=email_id).execute()
            return [TextContent(type="text", text=f"✅ Email permanently deleted")]
        else:
            service.users().messages().trash(userId='me', id=email_id).execute()
            return [TextContent(type="text", text=f"✅ Email moved to trash")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to delete email: {str(e)}")]

async def handle_reply_to_email(service, args):
    """Reply to an email"""
    email_id = args["email_id"]
    reply_body = args["body"]
    
    try:
        # Get original message
        original = service.users().messages().get(
            userId='me',
            id=email_id,
            format='metadata',
            metadataHeaders=['From', 'Subject', 'Message-ID']
        ).execute()
        
        headers = {h['name']: h['value'] for h in original['payload']['headers']}
        
        # Create reply
        message = MIMEText(reply_body)
        message['to'] = headers.get('From')
        message['subject'] = 'Re: ' + headers.get('Subject', '')
        message['In-Reply-To'] = headers.get('Message-ID', '')
        message['References'] = headers.get('Message-ID', '')
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        sent_message = service.users().messages().send(
            userId='me',
            body={'raw': raw_message, 'threadId': original['threadId']}
        ).execute()
        
        return [TextContent(type="text", text=f"✅ Reply sent successfully!\nMessage ID: {sent_message['id']}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to send reply: {str(e)}")]

async def handle_create_draft(service, args):
    """Create email draft"""
    to = args["to"]
    subject = args["subject"]
    body = args["body"]
    
    try:
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        draft = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': raw_message}}
        ).execute()
        
        return [TextContent(type="text", text=f"✅ Draft created successfully!\nDraft ID: {draft['id']}")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to create draft: {str(e)}")]

async def handle_list_labels(service, args):
    """List all Gmail labels"""
    try:
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        if not labels:
            return [TextContent(type="text", text="No labels found")]
        
        output = "🏷️  Gmail Labels:\n\n"
        for label in labels:
            output += f"• {label['name']} (ID: {label['id']})\n"
        
        return [TextContent(type="text", text=output)]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to list labels: {str(e)}")]

async def handle_add_label(service, args):
    """Add label to email"""
    email_id = args["email_id"]
    label_name = args["label"]
    
    try:
        # Get all labels to find ID
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])
        
        label_id = None
        for label in labels:
            if label['name'].lower() == label_name.lower():
                label_id = label['id']
                break
        
        if not label_id:
            return [TextContent(type="text", text=f"❌ Label '{label_name}' not found")]
        
        service.users().messages().modify(
            userId='me',
            id=email_id,
            body={'addLabelIds': [label_id]}
        ).execute()
        
        return [TextContent(type="text", text=f"✅ Label '{label_name}' added to email")]
    except Exception as e:
        return [TextContent(type="text", text=f"❌ Failed to add label: {str(e)}")]

async def main():
    """Run the MCP server"""
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
