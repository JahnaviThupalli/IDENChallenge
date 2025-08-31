import json
import os
from typing import Optional, Dict, Any
from playwright.sync_api import BrowserContext, Page
from config import Config

class SessionManager:
    def __init__(self, context: BrowserContext):
        self.context = context
        self.session_file = Config.SESSION_FILE
    
    def save_session(self) -> None:
        """Save current session storage to file"""
        try:
            # Get session storage from the first page
            pages = self.context.pages
            if pages:
                storage = pages[0].evaluate("() => JSON.stringify(sessionStorage)")
                session_data = {
                    'session_storage': json.loads(storage) if storage else {},
                    'cookies': self.context.cookies()
                }
                
                with open(self.session_file, 'w') as f:
                    json.dump(session_data, f, indent=2)
                print("Session saved successfully")
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def load_session(self) -> bool:
        """Load session from file and apply to context"""
        try:
            if not os.path.exists(self.session_file):
                return False
            
            with open(self.session_file, 'r') as f:
                session_data = json.load(f)
            
            # Apply cookies
            if session_data.get('cookies'):
                self.context.add_cookies(session_data['cookies'])
            
            # Apply session storage on first page load
            def set_session_storage(page: Page):
                storage = session_data.get('session_storage', {})
                for key, value in storage.items():
                    page.evaluate(f"sessionStorage.setItem('{key}', '{value}')")
            
            self.context.on('page', set_session_storage)
            
            print("Session loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading session: {e}")
            return False
    
    def session_exists(self) -> bool:
        """Check if session file exists and is valid"""
        return os.path.exists(self.session_file)
    
    def clear_session(self) -> None:
        """Clear saved session"""
        try:
            if os.path.exists(self.session_file):
                os.remove(self.session_file)
                print("Session cleared")
        except Exception as e:
            print(f"Error clearing session: {e}")
