from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional, TypedDict
import streamlit as st
from ..utlis.cache_drcorator import cache_result
from ..utlis.api_key_manager import YouTubeKeyManager

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

def get_youtube_client() -> Optional[object]:
    """
    Initialize YouTube API client.
    
    Returns:
        Optional[object]: YouTube API client or None if initialization fails
    """
    key_manager = YouTubeKeyManager()
    api_key = key_manager.get_active_key()
    
    if not api_key:
        st.error("No available API keys")
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

@cache_result(duration_hours=24)
def analyze_keyword_realtime(keyword: str) -> Optional[Dict]:
    """Analyze keyword in real-time"""
    try:
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
        
        return {
            'total_results': search_response['pageInfo']['totalResults'],
            'competition': 'Low' if int(search_response['pageInfo']['totalResults']) < 1000 else 'Medium',
            'top_channels': [item['snippet']['channelTitle'] for item in search_response.get('items', [])]
        }
        
    except Exception as e:
        st.error(f"Keyword analysis error: {str(e)}")
        return None

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
