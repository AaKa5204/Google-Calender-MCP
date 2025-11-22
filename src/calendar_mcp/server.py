"""Google Calendar MCP Server"""
import asyncio
from datetime import datetime, timedelta
from typing import Any
from mcp.server import Server
from mcp.types import Tool, TextContent
import mcp.server.stdio
from .auth import get_calendar_service

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
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """Handle tool calls"""
    try:
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
    
    created_event = service.events().insert(calendarId='primary', body=event).execute()
    
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
