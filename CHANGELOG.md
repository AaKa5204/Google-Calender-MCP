# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-22

### Added
- Initial release
- List calendar events (today, tomorrow, this week, next week, custom ranges)
- Create new calendar events with title, time, location, attendees
- Delete calendar events by ID
- Find free time slots in calendar
- Search events by keyword
- OAuth 2.0 authentication with Google
- Automatic token refresh
- MCP server implementation using FastMCP

### Security
- Credentials stored securely in user home directory
- Token auto-refresh for seamless experience
- .gitignore configured to prevent credential leaks

## [Unreleased]

### Planned Features
- Update/modify existing events
- Recurring event support
- Multiple calendar support
- Event reminders
- All-day events
- Better natural language date parsing
- Event color customization
- Calendar sharing management
