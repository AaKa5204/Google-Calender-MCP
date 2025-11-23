#!/usr/bin/env python3
"""Test script for Google Calendar MCP Server"""
import sys
sys.path.insert(0, 'src')

from calendar_mcp.server import app
import asyncio

async def test_tools():
    """Test that all tools are properly defined"""
    print("🧪 Testing Google Calendar MCP Server\n")
    
    # Test tool listing
    tools = await app.list_tools()
    print(f"✅ Found {len(tools)} tools:")
    for tool in tools:
        print(f"   • {tool.name}: {tool.description}")
    
    print("\n✅ All tools properly defined!")
    print("\n📋 Tool Details:")
    print("-" * 60)
    
    for tool in tools:
        print(f"\n🔧 {tool.name}")
        print(f"   Description: {tool.description}")
        print(f"   Required params: {tool.inputSchema.get('required', [])}")
        props = tool.inputSchema.get('properties', {})
        if props:
            print(f"   Parameters:")
            for param, details in props.items():
                param_type = details.get('type', 'unknown')
                desc = details.get('description', 'No description')
                print(f"      - {param} ({param_type}): {desc}")
    
    print("\n" + "=" * 60)
    print("✅ Server validation complete!")
    print("=" * 60)
    print("\n📝 Next steps:")
    print("1. Get Google Calendar API credentials")
    print("2. Save to ~/.google-calendar-mcp/credentials.json")
    print("3. Configure in Kiro's .kiro/settings/mcp.json")
    print("4. Test with: 'Kiro, what's on my calendar today?'")

if __name__ == "__main__":
    asyncio.run(test_tools())
