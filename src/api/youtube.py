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
    """Find similar professional EDM tracks"""
    try:
        youtube = get_youtube_client()
        if not youtube:
            return []
        
        # Create search query with verified artists
        verified_artists = {
            "Future House": ["Oliver Heldens", "Don Diablo", "Tchami"],
            "Tech House": ["Fisher", "Chris Lake", "John Summit"],
            "Bass House": ["Jauz", "AC Slater", "Joyryde"],
            "Deep House": ["Lane 8", "Yotto", "Ben Böhmer"],
            "Progressive House": ["Eric Prydz", "Cristoph", "Artbat"]
        }
        
        artists = verified_artists.get(genre, [])
        search_results = []
        
        for artist in artists:
            query = f"{artist} {genre} {track_features['bpm']}bpm"
            response = youtube.search().list(
                q=query,
                part='snippet',
                type='video',
                videoCategoryId='10',
                maxResults=3,
                videoEmbeddable='true'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in response['items']]
            
            # Get detailed video information
            videos = youtube.videos().list(
                part='statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            for video, search_result in zip(videos['items'], response['items']):
                if int(video['statistics'].get('viewCount', 0)) > 10000:  # Filter low-quality content
                    search_results.append({
                        'title': search_result['snippet']['title'],
                        'channel': search_result['snippet']['channelTitle'],
                        'url': f"https://youtube.com/watch?v={video['id']}",
                        'thumbnail': search_result['snippet']['thumbnails']['medium']['url'],
                        'views': int(video['statistics'].get('viewCount', 0)),
                        'likes': int(video['statistics'].get('likeCount', 0))
                    })
        
        return sorted(search_results, key=lambda x: x['views'], reverse=True)[:5]
        
    except Exception as e:
        st.error(f"YouTube API error: {str(e)}")
        return []
