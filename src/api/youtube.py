from googleapiclient.discovery import build
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Optional, TypedDict
import streamlit as st
import time

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

EDM_LABELS = {
    "Future House": [
        "Future House Music",
        "Hexagon",
        "Spinnin' Records",
        "Musical Freedom",
        "STMPD RCRDS"
    ],
    "Tech House": [
        "FISHER",
        "Insomniac Records",
        "Night Bass",
        "Confession",
        "Repopulate Mars"
    ],
    "Bass House": [
        "Night Bass",
        "Confession",
        "Bite This!",
        "Monstercat",
        "Dim Mak"
    ],
    "Progressive House": [
        "Anjunabeats",
        "Protocol Recordings",
        "Armada Music",
        "Size Records",
        "Axtone"
    ]
}

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
    """Find similar tracks from top EDM labels"""
    try:
        youtube = get_youtube_client()
        if not youtube:
            return []
        
        all_tracks = []
        
        # Search in relevant labels
        labels = EDM_LABELS.get(genre, EDM_LABELS["Future House"])
        for label in labels:
            search_query = f"{label} {genre} {track_features['bpm']}bpm"
            
            search_response = youtube.search().list(
                q=search_query,
                part='snippet',
                type='video',
                videoCategoryId='10',  # Music category
                maxResults=3,
                order='viewCount'
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            if video_ids:
                # Get detailed video information
                videos_response = youtube.videos().list(
                    part='statistics,contentDetails',
                    id=','.join(video_ids)
                ).execute()
                
                # Filter and add tracks
                for video, search_result in zip(videos_response['items'], search_response['items']):
                    if is_valid_track(video, search_result):
                        all_tracks.append({
                            'title': search_result['snippet']['title'],
                            'channel': search_result['snippet']['channelTitle'],
                            'url': f"https://youtube.com/watch?v={video['id']}",
                            'thumbnail': search_result['snippet']['thumbnails']['medium']['url'],
                            'views': int(video['statistics'].get('viewCount', 0)),
                            'likes': int(video['statistics'].get('likeCount', 0)),
                            'label': label
                        })
            
            time.sleep(0.1)  # Respect API limits
        
        # Sort by views and return top 5
        return sorted(all_tracks, key=lambda x: x['views'], reverse=True)[:5]
        
    except Exception as e:
        st.error(f"YouTube API error: {str(e)}")
        return []

def is_valid_track(video: Dict, search_result: Dict) -> bool:
    """Validate if the track meets quality criteria"""
    title = search_result['snippet']['title'].lower()
    views = int(video['statistics'].get('viewCount', 0))
    
    # Check if it's a music track (not a mix or playlist)
    if any(x in title for x in ['mix', 'playlist', 'compilation', 'best of']):
        return False
        
    # Check minimum views
    if views < 10000:
        return False
        
    # Check if it's from a verified channel
    if 'official' not in title and 'premiere' not in title:
        return False
        
    return True
