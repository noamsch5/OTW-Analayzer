import streamlit as st
from typing import Optional
from datetime import datetime, timedelta
import json
import os

class YouTubeKeyManager:
    def __init__(self):
        self.keys = st.secrets.get("YOUTUBE_API_KEYS", [])
        self.current_key_index = 0
        self.usage = {}
        self.last_reset = datetime.now()
        self._load_usage()
    
    def _load_usage(self):
        """Load key usage from cache"""
        cache_file = "cache/key_usage.json"
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                data = json.load(f)
                if datetime.fromisoformat(data['timestamp']) + timedelta(days=1) > datetime.now():
                    self.usage = data['usage']
                else:
                    self.usage = {key: 0 for key in self.keys}
        else:
            self.usage = {key: 0 for key in self.keys}
    
    def _save_usage(self):
        """Save key usage to cache"""
        cache_file = "cache/key_usage.json"
        os.makedirs("cache", exist_ok=True)
        with open(cache_file, 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'usage': self.usage
            }, f)
    
    def get_active_key(self) -> Optional[str]:
        """Get current active API key"""
        if not self.keys:
            return None
            
        # Reset usage if 24 hours have passed
        if datetime.now() - self.last_reset > timedelta(days=1):
            self.usage = {key: 0 for key in self.keys}
            self.last_reset = datetime.now()
            self._save_usage()
        
        # Find key with lowest usage
        current_key = min(self.usage.items(), key=lambda x: x[1])[0]
        return current_key
    
    def increment_usage(self, key: str, units: int = 100):
        """Track API usage"""
        self.usage[key] = self.usage.get(key, 0) + units
        self._save_usage()
