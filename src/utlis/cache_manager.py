import functools
from datetime import datetime, timedelta
import json
import os

def cache_result(duration_hours: int = 24):
    """Cache decorator for API results"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            cache_dir = "cache"
            os.makedirs(cache_dir, exist_ok=True)
            
            # Create cache key
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            cache_file = os.path.join(cache_dir, f"{cache_key}.json")
            
            # Check cache
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data['timestamp']) + timedelta(hours=duration_hours) > datetime.now():
                        return data['result']
            
            # Get fresh result
            result = func(*args, **kwargs)
            
            # Save to cache
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                }, f)
            
            return result
        return wrapper
    return decorator
