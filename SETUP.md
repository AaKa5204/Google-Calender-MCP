# Setup Guide

Complete step-by-step guide to get your Google Calendar MCP server running.

## Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- A Google account
- Kiro IDE (or any MCP-compatible client)

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/google-calendar-mcp.git
cd google-calendar-mcp
```

## Step 2: Install Dependencies

```bash
pip install -e .
```

This installs:
- `mcp` - Model Context Protocol SDK
- `google-auth` - Google authentication
- `google-api-python-client` - Google Calendar API
- `python-dateutil` - Date parsing

## Step 3: Get Google Calendar API Credentials

### 3.1 Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name it "Calendar MCP" (or anything you like)
4. Click "Create"

### 3.2 Enable Calendar API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google Calendar API"
3. Click on it and press "Enable"

### 3.3 Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External
   - App name: "Calendar MCP"
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue" through the rest
4. Back to "Create OAuth client ID":
   - Application type: "Desktop app"
   - Name: "Calendar MCP Client"
   - Click "Create"
5. Click "Download JSON"

### 3.4 Save Credentials

```bash
# Create the config directory
mkdir -p ~/.google-calendar-mcp

# Move the downloaded file
mv ~/Downloads/client_secret_*.json ~/.google-calendar-mcp/credentials.json
```

## Step 4: Configure Kiro

### Option A: Workspace Configuration (Recommended)

Create or edit `.kiro/settings/mcp.json` in your workspace:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["-m", "calendar_mcp.server"],
      "cwd": "/absolute/path/to/google-calendar-mcp",
      "disabled": false,
      "autoApprove": []
    }
  }
}
```

Replace `/absolute/path/to/google-calendar-mcp` with your actual path.

### Option B: Global Configuration

Edit `~/.kiro/settings/mcp.json`:

```json
{
  "mcpServers": {
    "google-calendar": {
      "command": "google-calendar-mcp",
      "disabled": false
    }
  }
}
```

## Step 5: First Run Authentication

1. Restart Kiro or reconnect the MCP server
2. In Kiro, try: "What's on my calendar today?"
3. A browser window will open
4. Sign in to your Google account
5. Click "Allow" to grant calendar access
6. The token is saved to `~/.google-calendar-mcp/token.json`

You're done! The server is now authenticated and ready to use.

## Verification

Test that everything works:

```
You: "Kiro, list my calendar events for today"
```

You should see your calendar events or "No events found for today".

## Troubleshooting

### "credentials.json not found"
- Make sure you saved the file to `~/.google-calendar-mcp/credentials.json`
- Check the file exists: `ls ~/.google-calendar-mcp/`

### "Invalid grant" or "Token expired"
```bash
rm ~/.google-calendar-mcp/token.json
```
Then re-authenticate by using the server again.

### "Calendar API has not been used"
- Make sure you enabled the Calendar API in Google Cloud Console
- Wait a few minutes for it to propagate

### Server not connecting in Kiro
- Check the MCP Server view in Kiro's feature panel
- Look for error messages
- Verify the `cwd` path is correct in your config

### Import errors
```bash
pip install -e . --force-reinstall
```

## Security Notes

⚠️ **Never commit these files to Git:**
- `~/.google-calendar-mcp/credentials.json`
- `~/.google-calendar-mcp/token.json`

They contain sensitive authentication data. The `.gitignore` is already configured to exclude them.

## Uninstalling

To remove access:
1. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
2. Find "Calendar MCP" and click "Remove Access"
3. Delete the credentials:
   ```bash
   rm -rf ~/.google-calendar-mcp
   ```
