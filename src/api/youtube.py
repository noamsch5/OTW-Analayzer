from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional, TypedDict
import streamlit as st

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
    """Initialize YouTube API client."""
    try:
        api_key = st.secrets["YOUTUBE_API_KEY"]
        if not api_key:
            logger.error("YouTube API key not found in environment variables")
            return None
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        logger.error(f"Failed to initialize YouTube client: {str(e)}")
        return None

def find_similar_tracks(genre: str, track_features: Dict) -> List[Dict]:
    """Find similar tracks on YouTube based on track features"""
    try:
        youtube = get_youtube_client()
        if not youtube:
            return []
        
        # Create dynamic search query
        search_query = f"{genre} {track_features['bpm']}bpm"
        if 'key' in track_features:
            search_query += f" {track_features['key']}"
        
        # Search for tracks
        search_response = youtube.search().list(
            q=search_query,
            part='snippet,statistics',
            maxResults=8,
            type='video',
            videoEmbeddable='true',
            videoCategoryId='10'  # Music category
        ).execute()
        
        # Get video details
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        videos_response = youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()
        
        # Combine search and video details
        video_stats = {v['id']: v['statistics'] for v in videos_response['items']}
        
        return [{
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'url': f"https://youtube.com/watch?v={item['id']['videoId']}",
            'thumbnail': item['snippet']['thumbnails']['medium']['url'],
            'views': video_stats[item['id']['videoId']]['viewCount'],
            'likes': video_stats[item['id']['videoId']].get('likeCount', '0')
        } for item in search_response['items']]
        
    except Exception as e:
        st.error(f"YouTube API error: {str(e)}")
        return []
