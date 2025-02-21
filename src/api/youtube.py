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
    """Find similar tracks with enhanced matching"""
    try:
        youtube = get_youtube_client()
        if not youtube:
            return []
        
        # Create targeted search query
        search_query = (
            f"{genre} {track_features['bpm']}bpm "
            f"{track_features['key']} music"
        )
        
        search_response = youtube.search().list(
            q=search_query,
            part='snippet',
            maxResults=5,
            type='video',
            videoCategoryId='10',  # Music category
            videoEmbeddable='true',
            order='relevance'
        ).execute()
        
        # Get video IDs
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        
        # Get detailed video information
        videos_response = youtube.videos().list(
            part='statistics,contentDetails',
            id=','.join(video_ids)
        ).execute()
        
        # Combine search results with video details
        video_details = {v['id']: v for v in videos_response['items']}
        
        similar_tracks = []
        for item in search_response['items']:
            video_id = item['id']['videoId']
            if video_id in video_details:
                stats = video_details[video_id]['statistics']
                similar_tracks.append({
                    'title': item['snippet']['title'],
                    'channel': item['snippet']['channelTitle'],
                    'url': f"https://youtube.com/watch?v={video_id}",
                    'thumbnail': item['snippet']['thumbnails']['medium']['url'],
                    'views': int(stats.get('viewCount', 0)),
                    'likes': int(stats.get('likeCount', 0)),
                    'engagement': calculate_engagement(stats)
                })
        
        return sorted(similar_tracks, key=lambda x: x['engagement'], reverse=True)
        
    except Exception as e:
        st.error(f"YouTube API error: {str(e)}")
        return []

def calculate_engagement(stats: Dict) -> float:
    """Calculate engagement score"""
    views = int(stats.get('viewCount', 0))
    likes = int(stats.get('likeCount', 0))
    comments = int(stats.get('commentCount', 0))
    
    if views == 0:
        return 0
        
    return (likes + comments * 2) / views
