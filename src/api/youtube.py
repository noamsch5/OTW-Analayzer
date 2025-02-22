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

EDM_CHANNELS = {
    "Future House": [
        "UCXvSeBDvzmPO05k-0RyB34g",  # Future House Music
        "UC3xS7KD-nL8tXwxBnbUYzBQ",  # Spinnin' Records
        "UC7BXWSDNQHwadVg6FJzFdqQ",  # Musical Freedom
    ],
    "Tech House": [
        "UC_kRDKYrUlrbtrSiyu5Tflg",  # Insomniac Records
        "UCu0qfYgxEiWHWUT5UNPVPoQ",  # Night Bass
        "UC9DunKv-AYe4mqTYWWeCOYg",  # Confession
    ],
    "Bass House": [
        "UCu0qfYgxEiWHWUT5UNPVPoQ",  # Night Bass
        "UC_kRDKYrUlrbtrSiyu5Tflg",  # Insomniac Records
        "UCgeRr_n3GuhMTnKh1HFhgQA",  # Bite This
    ],
    "Progressive House": [
        "UCGZXYc32ri4D0gSLPf2pZXQ",  # Anjunabeats
        "UC7burYeHNOvYzf0A9GHJV_A",  # Protocol Recordings
        "UC0n9KQkadSzQyeT5qR0Gwgw",  # Armada Music
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
    """Find similar tracks from top EDM channels"""
    try:
        # Check cache first
        cache_key = f"similar_{genre}_{track_features['bpm']}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

        youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
        all_tracks = []
        
        # Search in relevant channels
        channels = EDM_CHANNELS.get(genre, EDM_CHANNELS["Future House"])
        
        for channel_id in channels:
            try:
                # Search within channel
                search_response = youtube.search().list(
                    channelId=channel_id,
                    q=f"{genre} {track_features['bpm']}",
                    part='snippet',
                    type='video',
                    videoCategoryId='10',
                    maxResults=3,
                    order='viewCount'
                ).execute()
                
                video_ids = [item['id']['videoId'] for item in search_response['items']]
                
                if video_ids:
                    # Get detailed video information
                    videos_response = youtube.videos().list(
                        part='statistics',
                        id=','.join(video_ids)
                    ).execute()
                    
                    # Combine search results with statistics
                    for video, search_result in zip(videos_response['items'], search_response['items']):
                        all_tracks.append({
                            'title': search_result['snippet']['title'],
                            'channel': search_result['snippet']['channelTitle'],
                            'url': f"https://youtube.com/watch?v={video['id']}",
                            'thumbnail': search_result['snippet']['thumbnails']['medium']['url'],
                            'views': int(video['statistics'].get('viewCount', 0)),
                            'likes': int(video['statistics'].get('likeCount', 0))
                        })
                
                time.sleep(0.1)  # Respect API limits
                
            except Exception as e:
                continue
        
        # Sort by views and return top 5
        similar_tracks = sorted(all_tracks, key=lambda x: x['views'], reverse=True)[:5]
        
        # Cache the results
        save_to_cache(cache_key, similar_tracks)
        return similar_tracks
        
    except Exception as e:
        st.error(f"Error finding similar tracks: {str(e)}")
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
