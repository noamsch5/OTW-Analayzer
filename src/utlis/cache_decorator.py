import functools
from datetime import datetime, timedelta
import json
import os

def cache_result(cache_duration: timedelta = timedelta(hours=24)):
    """Cache function results to avoid API calls"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            cache_file = f"cache/{cache_key}.json"
            
            # Check cache
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if datetime.fromisoformat(data['timestamp']) + cache_duration > datetime.now():
                        return data['result']
            
            # Get fresh result
            result = func(*args, **kwargs)
            
            # Save to cache
            os.makedirs("cache", exist_ok=True)
            with open(cache_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'result': result
                }, f)
            
            return result
        return wrapper
    return decorator
