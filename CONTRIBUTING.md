# Contributing to Google Calendar MCP

Thanks for your interest in contributing! This project welcomes contributions of all kinds.

## How to Contribute

### Reporting Bugs

Open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (OS, Python version)

### Suggesting Features

Open an issue describing:
- The feature you'd like
- Why it would be useful
- How it might work

### Code Contributions

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit with clear messages
6. Push and open a pull request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/google-calendar-mcp.git
cd google-calendar-mcp

# Install in development mode
pip install -e .

# Make changes and test
python -m calendar_mcp.server
```

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep functions focused and small

## Testing

Before submitting:
- Test all existing features still work
- Test your new feature with Kiro
- Check for Python errors

## Ideas for Contributions

- Add recurring event support
- Implement event updates/modifications
- Add support for multiple calendars
- Improve date/time parsing
- Add event reminders
- Support for all-day events
- Better error messages
- Unit tests
- Integration with Google Meet
- Export events to different formats

## Questions?

Open an issue or discussion - happy to help!
