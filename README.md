# Google Calendar MCP Server

🤖 An MCP (Model Context Protocol) server that gives AI assistants like Kiro direct access to your Google Calendar.

Ask your AI to check your schedule, create events, find free time, and manage your calendar - all through natural conversation.

## ✨ Features

- 📅 **List Events** - View events for today, tomorrow, this week, or custom ranges
- ➕ **Create Events** - Add new calendar events with details
- 🗑️ **Delete Events** - Remove events by ID
- 🔍 **Search Events** - Find events by keyword
- 🕐 **Find Free Slots** - Discover available time slots

## 🚀 Quick Start

### 1. Clone and Install

```bash
git clone https://github.com/YOUR_USERNAME/google-calendar-mcp.git
cd google-calendar-mcp
pip install -e .
```

### 2. Get Google Credentials

See [SETUP.md](SETUP.md) for detailed instructions on getting Google Calendar API credentials.

**Quick version:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable Calendar API → Create OAuth credentials
3. Download and save to `~/.google-calendar-mcp/credentials.json`

### 3. Configure Kiro

Add to `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["-m", "calendar_mcp.server"],
      "cwd": "/path/to/google-calendar-mcp",
      "disabled": false
    }
  }
}
```

### 4. Authenticate

First use will open your browser to sign in to Google. That's it!

## Usage Examples

### List Today's Events
```
You: "Kiro, what's on my calendar today?"
```

### Create an Event
```
You: "Kiro, schedule a team meeting tomorrow at 2 PM for 1 hour"
```

### Find Free Time
```
You: "Kiro, when am I free for a 30-minute meeting this week?"
```

### Search Events
```
You: "Kiro, find all my dentist appointments"
```

### Delete an Event
```
You: "Kiro, delete the event with ID abc123xyz"
```

## Tools Available

### list_events
List calendar events for a time range.

**Parameters:**
- `time_range`: "today", "tomorrow", "this_week", "next_week", or "custom"
- `max_results`: Maximum events to return (default: 10)
- `start_date`: For custom range (optional)
- `end_date`: For custom range (optional)

### create_event
Create a new calendar event.

**Parameters:**
- `summary`: Event title (required)
- `start_time`: Start time (required)
- `end_time`: End time (required)
- `description`: Event description (optional)
- `location`: Event location (optional)
- `attendees`: List of email addresses (optional)

### delete_event
Delete a calendar event.

**Parameters:**
- `event_id`: ID of event to delete (required)

### find_free_slots
Find available time slots.

**Parameters:**
- `duration_minutes`: Duration needed (default: 60)
- `days_ahead`: Days to search (default: 7)
- `work_hours_only`: Only 9 AM - 5 PM (default: true)

### search_events
Search for events by keyword.

**Parameters:**
- `query`: Search term (required)
- `max_results`: Max results (default: 10)

## Troubleshooting

### "credentials.json not found"
Make sure you've downloaded OAuth credentials from Google Cloud Console and saved them to `~/.google-calendar-mcp/credentials.json`

### "Invalid grant" or "Token expired"
Delete `~/.google-calendar-mcp/token.json` and re-authenticate

### Permission errors
Ensure the Google Calendar API is enabled in your Google Cloud project

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The token gives access to your calendar - keep it secure
- Revoke access anytime from your [Google Account settings](https://myaccount.google.com/permissions)

## Development

Project structure:
```
google-calendar-mcp/
├── pyproject.toml
├── README.md
└── src/
    └── calendar_mcp/
        ├── __init__.py
        ├── server.py      # MCP server implementation
        └── auth.py        # Google OAuth handling
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Ideas for contributions:
- Recurring events support
- Event updates/modifications
- Multiple calendar support
- Better natural language parsing
- Unit tests

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [Google Calendar API](https://developers.google.com/calendar)

## ⭐ Star This Repo

If you find this useful, give it a star! It helps others discover the project.

---

**Made with ❤️ for the MCP community**
