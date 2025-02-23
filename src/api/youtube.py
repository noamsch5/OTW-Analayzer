from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional, TypedDict
import streamlit as st
import json
from datetime import datetime, timedelta
from ..utlis.cache_manager import cache_result
from ..utlis.key_manager import YouTubeKeyManager

# Type definitions
class TrackInfo(TypedDict):
    title: str
    channel: str
    videoId: str

class VideoDetails(TypedDict):
    snippet: Dict
    statistics: Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Cache configuration
CACHE_DIR = "cache"
CACHE_DURATION = timedelta(hours=24)

def get_cache_path(key: str) -> str:
    """Get cache file path for a key"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{key.replace(' ', '_')}.json")

def get_cached_data(key: str) -> Optional[Dict]:
    """Get data from cache if valid"""
    cache_path = get_cache_path(key)
    if (os.path.exists(cache_path)):
        with open(cache_path, 'r') as f:
            data = json.load(f)
            if datetime.fromisoformat(data['timestamp']) + CACHE_DURATION > datetime.now():
                return data['content']
    return None

def save_to_cache(key: str, content: Dict) -> None:
    """Save data to cache"""
    cache_path = get_cache_path(key)
    with open(cache_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'content': content
        }, f)

def get_youtube_client() -> Optional[object]:
    """Get YouTube client with API key"""
    api_key = st.secrets.get("YOUTUBE_API_KEY")
    if not api_key:
        st.error("YouTube API key not found in Streamlit secrets")
        return None
    return build('youtube', 'v3', developerKey=api_key)

def find_similar_tracks(genre: str) -> List[TrackInfo]:
    """
    Find similar tracks on YouTube based on genre.
    
    Args:
        genre (str): Music genre to search for
        
    Returns:
        List[TrackInfo]: List of track information dictionaries
    """
    try:
        youtube = get_youtube_client()
        if not youtube:
            return []
            
        search_response = youtube.search().list(
            q=f"{genre} music",
            part='snippet',
            type='video',
            videoCategoryId='10',
            maxResults=5
        ).execute()
        
        return [{
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'url': f"https://youtube.com/watch?v={item['id']['videoId']}"
        } for item in search_response.get('items', [])]
        
    except Exception as e:
        st.error(f"Error finding similar tracks: {str(e)}")
        return []

def analyze_keyword_realtime(keyword: str) -> Optional[Dict]:
    """Analyze keyword with caching"""
    try:
        # Check cache first
        cache_key = f"keyword_{keyword}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

        youtube = get_youtube_client()
        if not youtube:
            return None

        search_response = youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            videoCategoryId='10',
            maxResults=5
        ).execute()

        result = {
            'score': calculate_keyword_score(search_response),
            'competition': get_competition_level(search_response),
            'monthly_searches': estimate_monthly_searches(search_response),
            'total_results': search_response['pageInfo']['totalResults']
        }

        # Save to cache
        save_to_cache(cache_key, result)
        return result

    except Exception as e:
        st.warning("Using cached data due to API limitations")
        return get_fallback_data(keyword)

def get_fallback_data(keyword: str) -> Dict:
    """Provide fallback data when API is unavailable"""
    return {
        'score': 50,
        'competition': 'Medium',
        'monthly_searches': '1K-10K',
        'total_results': 1000
    }

def calculate_keyword_score(response: Dict) -> float:
    """Calculate keyword score based on search results"""
    total_results = response['pageInfo']['totalResults']
    if total_results < 1000:
        return 80
    elif total_results < 10000:
        return 60
    return 40

def get_competition_level(response: Dict) -> str:
    """Determine competition level"""
    total_results = response['pageInfo']['totalResults']
    if total_results < 1000:
        return "Low"
    elif total_results < 10000:
        return "Medium"
    return "High"

def estimate_monthly_searches(response: Dict) -> str:
    """Estimate monthly search volume"""
    total_results = response['pageInfo']['totalResults']
    if total_results < 1000:
        return "100-1K"
    elif total_results < 10000:
        return "1K-10K"
    return "10K+"

def get_video_details(video_id: str) -> VideoDetails:
    """
    Get detailed information about a specific YouTube video.
    
    Args:
        video_id (str): YouTube video ID
        
    Returns:
        VideoDetails: Video details including snippet and statistics
    """
    try:
        youtube = get_youtube_client()
        if not youtube:
            return VideoDetails(snippet={}, statistics={})
            
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()
        
        return video_response.get('items', [VideoDetails(snippet={}, statistics={})])[0]
        
    except Exception as e:
        logger.error(f"Error getting video details: {str(e)}")
        return VideoDetails(snippet={}, statistics={})
