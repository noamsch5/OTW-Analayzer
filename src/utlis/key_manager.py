import streamlit as st
from typing import Optional
from datetime import datetime, timedelta

class YouTubeKeyManager:
    def __init__(self):
        self.keys = st.secrets.get("YOUTUBE_API_KEYS", [])
        self.current_index = 0
        
    def get_active_key(self) -> Optional[str]:
        """Get current active API key"""
        if not self.keys:
            return None
            
        key = self.keys[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.keys)
        return key
