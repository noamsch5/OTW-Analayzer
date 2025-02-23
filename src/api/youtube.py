from googleapiclient.discovery import build
import os
import logging
from typing import List, Dict, Optional, TypedDict
import streamlit as st
import json
import time
from datetime import datetime, timedelta

# Type definitions and configuration
class TrackInfo(TypedDict):
    title: str
    channel: str
    videoId: str

class VideoDetails(TypedDict):
    snippet: Dict
    statistics: Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CACHE_DIR = "cache"
CACHE_DURATION = timedelta(hours=24)

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

# Add cache configuration
def get_cache_path(key: str) -> str:
    """Get cache file path for a key"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{key.replace(' ', '_')}.json")

def get_cached_data(key: str) -> Optional[Dict]:
    """Get data from cache if valid"""
    cache_path = get_cache_path(key)
    if os.path.exists(cache_path):
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
    
    try:
        return build('youtube', 'v3', developerKey=api_key)
    except Exception as e:
        logger.error(f"Error initializing YouTube client: {str(e)}")
        return None

def find_similar_tracks(genre: str, track_features: Dict) -> List[Dict]:
    """Find similar tracks from top EDM channels and labels"""
    try:
        bpm = int(track_features.get('bpm', 128))
        cache_key = f"similar_{genre}_{bpm}"
        
        # Try cache first
        cached_data = get_cached_data(cache_key)
        if cached_data:
            logger.info("Returning cached similar tracks")
            return cached_data

        youtube = get_youtube_client()
        if not youtube:
            return []
        
        all_tracks = []
        
        # Try searching by channel first
        channels = EDM_CHANNELS.get(genre, EDM_CHANNELS["Future House"])
        labels = EDM_LABELS.get(genre, EDM_LABELS["Future House"])
        
        # First attempt: Search by channel
        for channel_id in channels[:1]:  # Try just one channel first to save quota
            try:
                search_response = youtube.search().list(
                    channelId=channel_id,
                    q=f"{genre}",  # Simplified search query
                    part='snippet',
                    type='video',
                    videoCategoryId='10',
                    maxResults=3,
                    order='viewCount'
                ).execute()
                
                for item in search_response.get('items', []):
                    track = {
                        'title': item['snippet']['title'],
                        'channel': item['snippet']['channelTitle'],
                        'url': f"https://youtube.com/watch?v={item['id']['videoId']}",
                        'thumbnail': item['snippet']['thumbnails']['medium']['url']
                    }
                    all_tracks.append(track)
                
            except Exception as e:
                logger.warning(f"Channel search failed, trying labels: {str(e)}")
        
        # If channel search didn't yield enough results, try labels
        if len(all_tracks) < 3:
            for label in labels[:2]:  # Try just two labels to save quota
                try:
                    search_response = youtube.search().list(
                        q=f"{label} {genre}",
                        part='snippet',
                        type='video',
                        videoCategoryId='10',
                        maxResults=2,
                        order='viewCount'
                    ).execute()
                    
                    for item in search_response.get('items', []):
                        track = {
                            'title': item['snippet']['title'],
                            'channel': item['snippet']['channelTitle'],
                            'url': f"https://youtube.com/watch?v={item['id']['videoId']}",
                            'thumbnail': item['snippet']['thumbnails']['medium']['url']
                        }
                        all_tracks.append(track)
                        
                except Exception:
                    continue
                
                time.sleep(0.1)  # Respect API limits
        
        if not all_tracks:
            return get_fallback_tracks(genre)
        
        # Take top 5 unique tracks
        seen = set()
        unique_tracks = []
        for track in all_tracks:
            if track['title'] not in seen:
                seen.add(track['title'])
                unique_tracks.append(track)
        
        similar_tracks = unique_tracks[:5]
        save_to_cache(cache_key, similar_tracks)
        return similar_tracks
        
    except Exception as e:
        logger.error(f"Error finding similar tracks: {str(e)}")
        return get_fallback_tracks(genre)

def get_fallback_tracks(genre: str) -> List<Dict]:
    """Get fallback tracks when API fails"""
    return [{
        'title': f'Example {genre} Track {i}',
        'channel': 'Sample Channel',
        'url': '#',
        'thumbnail': 'https://via.placeholder.com/120x90.png',
    } for i in range(1, 6)]

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

def analyze_keyword_realtime(keyword: str) -> Optional[Dict]:
    """Analyze keyword with caching"""
    try:
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
            maxResults=5,
            regionCode='US'
        ).execute()

        result = {
            'score': calculate_keyword_score(search_response),
            'competition': get_competition_level(search_response['pageInfo']['totalResults']),
            'monthly_searches': estimate_monthly_searches(search_response['pageInfo']['totalResults']),
            'suggestions': get_keyword_suggestions(keyword, youtube)
        }

        save_to_cache(cache_key, result)
        return result

    except Exception as e:
        logger.error(f"Keyword analysis error: {str(e)}")
        return get_fallback_data()

def calculate_keyword_score(search_response: Dict) -> float:
    """Calculate keyword potential score (0-100)"""
    total_results = search_response['pageInfo']['totalResults']
    video_ids = [item['id']['videoId'] for item in search_response['items']]
    if video_ids:
        videos_response = youtube.videos().list(
            part='statistics',
            id=','.join(video_ids)
        ).execute()
        
        views = []
        likes = []
        for video in videos_response['items']:
            stats = video['statistics']
            views.append(int(stats.get('viewCount', 0)))
            likes.append(int(stats.get('likeCount', 0)))
        
        avg_views = sum(views) / len(views) if views else 0
        engagement = sum(likes) / sum(views) if sum(views) > 0 else 0
        
        view_score = min(avg_views / 100000, 1.0) * 40
        competition_score = (1 - min(total_results / 10000, 1.0)) * 30
        engagement_score = min(engagement * 100, 1.0) * 30
        return view_score + competition_score + engagement_score
    return 0

def get_competition_level(total_results: int) -> str:
    """Determine keyword competition level"""
    if total_results < 1000:
        return "Low"
    elif total_results < 10000:
        return "Medium"
    return "High"

def estimate_monthly_searches(total_results: int) -> str:
    """Estimate monthly search volume"""
    if total_results < 1000:
        return "100-1K"
    elif total_results < 10000:
        return "1K-10K"
    elif total_results < 100000:
        return "10K-100K"
    return "100K+"

def get_keyword_suggestions(keyword: str, youtube) -> List[str]:
    """Get related keyword suggestions"""
    try:
        response = youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            maxResults=10,
            videoCategoryId='10'
        ).execute()
        
        suggestions = set()
        for item in response.get('items', []):
            title = item['snippet']['title'].lower()
            words = title.split()
            if len(words) > 2:
                suggestions.add(' '.join(words[:3]))
        
        return list(suggestions)[:5]
    except Exception:
        return []

def get_fallback_data() -> Dict:
    """Provide fallback data when API is unavailable"""
    return {
        'score': 50,
        'competition': 'Medium',
        'monthly_searches': '1K-10K',
        'suggestions': []
    }

def handle_quota_error(e: Exception) -> bool:
    """Check if error is due to quota exceeded"""
    error_message = str(e).lower()
    return 'quota' in error_message or 'rate limit' in error_message
