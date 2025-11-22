"""Google Calendar OAuth authentication"""
import os
import json
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Authenticate and return Google Calendar service"""
    creds = None
    token_path = Path.home() / '.google-calendar-mcp' / 'token.json'
    credentials_path = Path.home() / '.google-calendar-mcp' / 'credentials.json'
    
    # Create directory if it doesn't exist
    token_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing token
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)
    
    # Refresh or get new credentials
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}\n"
                    "Please download OAuth credentials from Google Cloud Console"
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save credentials
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('calendar', 'v3', credentials=creds)
