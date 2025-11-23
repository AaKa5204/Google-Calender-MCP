# Quick Start Guide

Get your Google Calendar MCP server running in 5 minutes!

## ✅ Step 1: Verify Setup (Already Done!)

The server is configured in `.kiro/settings/mcp.json`

## 🔑 Step 2: Get Google Credentials

### Option A: Quick Setup (5 minutes)

1. Go to https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable Google Calendar API:
   - Click "APIs & Services" → "Library"
   - Search "Google Calendar API"
   - Click "Enable"
4. Create credentials:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - If prompted, configure consent screen (External, add your email)
   - Application type: "Desktop app"
   - Name: "Calendar MCP"
   - Click "Create" and download JSON

5. Save the file:
```bash
mkdir -p ~/.google-calendar-mcp
mv ~/Downloads/client_secret_*.json ~/.google-calendar-mcp/credentials.json
```

### Option B: Detailed Instructions

See [SETUP.md](SETUP.md) for step-by-step with screenshots.

## 🔌 Step 3: Connect to Kiro

### Method 1: Restart Kiro (Easiest)
- Quit and reopen Kiro
- The server will auto-connect

### Method 2: Reconnect Server
1. Open Command Palette (Cmd+Shift+P)
2. Type "MCP"
3. Select "MCP: Reconnect Server"
4. Choose "google-calendar"

### Method 3: Use MCP Panel
1. Open Kiro's feature panel (sidebar)
2. Find "MCP Servers" section
3. Click reconnect icon next to "google-calendar"

## 🎉 Step 4: Test It!

Try these prompts in Kiro:

### Basic Tests
```
You: "Kiro, what's on my calendar today?"
You: "Kiro, list my events for this week"
```

### Create Events
```
You: "Kiro, schedule a team meeting tomorrow at 2 PM for 1 hour"
You: "Kiro, add 'Dentist appointment' on Friday at 10 AM"
```

### Find Free Time
```
You: "Kiro, when am I free for a 30-minute meeting this week?"
You: "Kiro, show me available time slots tomorrow"
```

### Search
```
You: "Kiro, find all my meetings with John"
You: "Kiro, search for 'dentist' in my calendar"
```

## 🔍 Troubleshooting

### "Server not connected"
- Check `.kiro/settings/mcp.json` exists
- Restart Kiro
- Check MCP Server panel for errors

### "credentials.json not found"
```bash
# Verify file exists
ls ~/.google-calendar-mcp/credentials.json

# If not, download from Google Cloud Console
```

### "Authentication failed"
```bash
# Delete token and re-authenticate
rm ~/.google-calendar-mcp/token.json
# Then try using the server again
```

### "Module not found"
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

### Check Server Status
Look in Kiro's MCP Server panel:
- 🟢 Green = Connected and working
- 🔴 Red = Error (click for details)
- ⚪ Gray = Disabled

## 📊 Verify It's Working

When you make your first request:
1. Browser will open automatically
2. Sign in to Google
3. Click "Allow" to grant calendar access
4. Token saved to `~/.google-calendar-mcp/token.json`
5. Future requests work automatically!

## 🎯 Example Session

```
You: "Kiro, what's on my calendar today?"

Kiro: "📅 Events for today:

• 9:00 AM - Team Standup
  ID: abc123xyz

• 2:00 PM - Project Review
  📍 Conference Room A
  ID: def456uvw

• 4:00 PM - 1-on-1 with Manager
  ID: ghi789rst"

You: "Kiro, schedule lunch with Sarah tomorrow at noon"

Kiro: "✅ Event created successfully!

📅 Lunch with Sarah
🕐 Tomorrow at 12:00 PM
ID: jkl012mno
Link: https://calendar.google.com/..."
```

## 🚀 You're Ready!

Your Google Calendar MCP server is now running. Try it out!

## 💡 Tips

- Event IDs are useful for deleting: "Delete event abc123xyz"
- Be specific with times: "2 PM" or "14:00"
- Natural language works: "next Tuesday", "tomorrow morning"
- You can add attendees: "Schedule meeting with john@example.com"

## 📚 More Info

- Full documentation: [README.md](README.md)
- Detailed setup: [SETUP.md](SETUP.md)
- Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Need help?** Open an issue on GitHub!
