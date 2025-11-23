#!/bin/bash

# Setup script for Google Calendar MCP Server with Kiro

echo "🚀 Setting up Google Calendar MCP Server..."

# Get the current directory
CURRENT_DIR="$(pwd)"

# Create Kiro settings directory
mkdir -p .kiro/settings

# Create MCP configuration
cat > .kiro/settings/mcp.json << EOF
{
  "mcpServers": {
    "google-calendar": {
      "command": "python",
      "args": ["-m", "calendar_mcp.server"],
      "cwd": "$CURRENT_DIR",
      "env": {
        "PYTHONPATH": "$CURRENT_DIR/src"
      },
      "disabled": false,
      "autoApprove": []
    }
  }
}
EOF

echo "✅ Created .kiro/settings/mcp.json"
echo ""
echo "📝 Configuration:"
echo "   Server name: google-calendar"
echo "   Working directory: $CURRENT_DIR"
echo ""
echo "🔑 Next steps:"
echo "1. Get Google Calendar API credentials from:"
echo "   https://console.cloud.google.com/"
echo ""
echo "2. Save credentials to:"
echo "   ~/.google-calendar-mcp/credentials.json"
echo ""
echo "3. Restart Kiro or reconnect the MCP server from:"
echo "   - MCP Server view in Kiro's feature panel"
echo "   - Or use Command Palette: 'MCP: Reconnect Server'"
echo ""
echo "4. Test with Kiro:"
echo "   'What's on my calendar today?'"
echo ""
echo "✨ Setup complete!"
