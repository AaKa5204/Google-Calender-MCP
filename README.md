# Google Calendar & Gmail MCP Server

🤖 An MCP (Model Context Protocol) server that gives AI assistants like Kiro direct access to your Google Calendar and Gmail.

Ask your AI to check your schedule, create events, send emails, manage your inbox - all through natural conversation.

## ✨ Features

### Calendar Features
- 📅 **List Events** - View events for today, tomorrow, this week, or custom ranges
- ➕ **Create Events** - Add new calendar events with attendees and optional email invites
- 🗑️ **Delete Events** - Remove events by ID
- 🔍 **Search Events** - Find events by keyword
- 🕐 **Find Free Slots** - Discover available time slots

### Gmail Features
- 📧 **Send Emails** - Send emails with HTML support, CC, BCC
- 📬 **List Emails** - Browse inbox, sent, drafts with filters
- 🔍 **Search Emails** - Advanced email search by sender, subject, date
- 📖 **Read Emails** - View full email content
- ✅ **Mark Emails** - Mark as read/unread
- 🗑️ **Delete Emails** - Trash or permanently delete
- 💬 **Reply to Emails** - Reply in email threads
- 📝 **Create Drafts** - Save email drafts
- 🏷️ **Manage Labels** - Organize emails with labels

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/AaKa5204/Google-Calender-MCP.git
cd Google-Calender-MCP
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required packages
pip install -r requirements.txt
```

### 3. Get Google API Credentials

**Step-by-step:**

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing)
3. Enable APIs:
   - Go to "APIs & Services" → "Enable APIs and Services"
   - Search and enable **Google Calendar API**
   - Search and enable **Gmail API**
4. Create OAuth credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Desktop app" as application type
   - Download the JSON file
5. Save credentials:
   ```bash
   mkdir -p ~/.google-calendar-mcp
   cp ~/Downloads/client_secret_*.json ~/.google-calendar-mcp/credentials.json
   ```

See [SETUP.md](SETUP.md) for detailed instructions with screenshots.

### 4. Configure Kiro IDE

Add to your `.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["-m", "calendar_mcp.server"],
      "cwd": "/absolute/path/to/Google-Calender-MCP",
      "disabled": false
    }
  }
}

```

**Important:** Replace `/absolute/path/to/Google-Calender-MCP` with your actual project path.

### 5. Restart MCP Server

1. Open Command Palette in Kiro (Cmd+Shift+P / Ctrl+Shift+P)
2. Search for "MCP"
3. Select "Reconnect MCP Server"

### 6. Authenticate

On first use, a browser window will open asking you to:
1. Sign in to your Google account
2. Grant Calendar and Gmail permissions
3. That's it! The token is saved for future use.

## 🎯 Usage Examples

### Calendar Examples

**List Today's Events:**
```
You: "What's on my calendar today?"
```

**Create an Event:**
```
You: "Schedule a team meeting tomorrow at 2 PM for 1 hour"
```

**Create Event with Invite:**
```
You: "Create a meeting with john@example.com at 3 PM today and send them an invite"
```

**Find Free Time:**
```
You: "When am I free for a 30-minute meeting this week?"
```

### Gmail Examples

**Send an Email:**
```
You: "Send an email to jane@example.com with subject 'Project Update' and tell her the project is on track"
```

**Check Inbox:**
```
You: "What's in my inbox?"
```

**Search Emails:**
```
You: "Find emails from john@example.com about the budget"
```

**Read an Email:**
```
You: "Read the email with ID abc123xyz"
```

**Reply to Email:**
```
You: "Reply to email abc123xyz and say thanks"
```

## 📋 Requirements

- Python 3.8 or higher
- Kiro IDE (or any MCP-compatible client)
- Google account
- Google Cloud project with Calendar and Gmail APIs enabled

## 🛠️ Available Tools

### Calendar Tools

#### list_events
List calendar events for a time range.
- `time_range`: "today", "tomorrow", "this_week", "next_week", or "custom"
- `max_results`: Maximum events to return (default: 10)
- `start_date`, `end_date`: For custom range (optional)

#### create_event
Create a new calendar event.
- `summary`: Event title (required)
- `start_time`, `end_time`: Event times (required)
- `description`: Event description (optional)
- `location`: Event location (optional)
- `attendees`: List of email addresses (optional)
- `send_invites`: Send email invitations (default: false)

#### delete_event
Delete a calendar event.
- `event_id`: ID of event to delete (required)

#### find_free_slots
Find available time slots.
- `duration_minutes`: Duration needed (default: 60)
- `days_ahead`: Days to search (default: 7)
- `work_hours_only`: Only 9 AM - 5 PM (default: true)

#### search_events
Search for events by keyword.
- `query`: Search term (required)
- `max_results`: Max results (default: 10)

### Gmail Tools

#### send_email
Send an email via Gmail.
- `to`: Recipient email (required)
- `subject`: Email subject (required)
- `body`: Email body (required)
- `html`: Whether body is HTML (default: false)
- `cc`, `bcc`: Additional recipients (optional)

#### list_emails
List emails from inbox, sent, or drafts.
- `folder`: "inbox", "sent", "drafts", "all" (default: inbox)
- `max_results`: Maximum emails (default: 10)
- `unread_only`: Only unread emails (default: false)

#### search_emails
Search emails by query.
- `query`: Search query (e.g., "from:user@example.com", "subject:meeting")
- `max_results`: Max results (default: 10)

#### read_email
Read full email content.
- `email_id`: Email message ID (required)

#### mark_email
Mark email as read/unread.
- `email_id`: Email message ID (required)
- `mark_as`: "read" or "unread" (required)

#### delete_email
Delete or trash an email.
- `email_id`: Email message ID (required)
- `permanent`: Permanently delete vs trash (default: false)

#### reply_to_email
Reply to an email.
- `email_id`: Email to reply to (required)
- `body`: Reply message (required)

#### create_draft
Create an email draft.
- `to`: Recipient (required)
- `subject`: Subject (required)
- `body`: Body (required)

#### list_labels
List all Gmail labels/folders.

#### add_label
Add label to an email.
- `email_id`: Email message ID (required)
- `label`: Label name (required)

## 🔧 Troubleshooting

### "credentials.json not found"
- Download OAuth credentials from Google Cloud Console
- Save to `~/.google-calendar-mcp/credentials.json`
- Make sure the path is correct

### "API has not been used in project" or "API is disabled"
- Go to Google Cloud Console
- Navigate to "APIs & Services" → "Library"
- Search and enable both **Google Calendar API** and **Gmail API**
- Wait a few minutes for changes to propagate

### "Invalid grant" or "Token expired"
```bash
rm ~/.google-calendar-mcp/token.json
```
Then restart the MCP server and re-authenticate

### MCP Server not connecting
- Check that the `cwd` path in mcp.json is correct (absolute path)
- Verify Python is in your PATH
- Check MCP server logs in Kiro
- Try reconnecting: Command Palette → "Reconnect MCP Server"

### Permission errors
- Ensure both Calendar and Gmail APIs are enabled in Google Cloud project
- Check that OAuth consent screen is configured
- Verify the credentials.json file is valid

## Security Notes

- Never commit `credentials.json` or `token.json` to version control
- The token gives access to your calendar - keep it secure
- Revoke access anytime from your [Google Account settings](https://myaccount.google.com/permissions)

## 📁 Project Structure

```
Google-Calender-MCP/
├── src/
│   └── calendar_mcp/
│       ├── __init__.py
│       ├── server.py      # MCP server with all tools
│       └── auth.py        # Google OAuth authentication
├── pyproject.toml         # Package configuration
├── requirements.txt       # Python dependencies
├── README.md             # This file
├── SETUP.md              # Detailed setup guide
├── CONTRIBUTING.md       # Contribution guidelines
└── test_server.py        # Test script
```

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Ideas for contributions:**
- Recurring events support
- Event updates/modifications
- Multiple calendar support
- Email attachments support
- Better natural language parsing
- Unit tests and integration tests
- Email templates
- Calendar sharing features

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details

## 🙏 Acknowledgments

- Built with [Model Context Protocol](https://modelcontextprotocol.io/)
- Uses [Google Calendar API](https://developers.google.com/calendar)

## ⭐ Star This Repo

If you find this useful, give it a star! It helps others discover the project.

---

**Made with ❤️ for the MCP community**
