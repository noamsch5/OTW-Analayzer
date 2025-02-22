from googleapiclient.discovery import build
import streamlit as st
from typing import Dict, List, Optional
import time
import json
import os
from datetime import datetime, timedelta

# Define EDM Labels dictionary
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

# Cache configuration
CACHE_DIR = "cache"
CACHE_DURATION = timedelta(hours=24)

def get_cache_path(key: str) -> str:
    """Get cache file path for a key"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)
    return os.path.join(CACHE_DIR, f"{key.replace(' ', '_')}.json")

def get_cached_data(key: str) -> Dict:
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

def analyze_keywords(genre: str, track_features: Dict) -> Dict:
    """Analyze keywords with caching"""
    try:
        cache_key = f"{genre}_{track_features['bpm']}_{track_features['key']}"
        cached_data = get_cached_data(cache_key)
        
        if cached_data:
            return cached_data
            
        # If not in cache, proceed with API call
        youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
        
        # Generate EDM-specific keywords
        base_keywords = [
            f"{genre}",
            f"{genre} {track_features['bpm']}bpm",
            f"{genre} {track_features['key']}",
            f"new {genre} 2024",
            f"{genre} official music",
            f"{genre} release",
            f"best {genre}",
            f"{genre} edm"
        ]
        
        # Add label-specific keywords
        for label in EDM_LABELS.get(genre, []):
            base_keywords.append(f"{label} {genre}")
        
        keyword_stats = {}
        
        for keyword in base_keywords:
            try:
                search_response = youtube.search().list(
                    q=keyword,
                    part='snippet',
                    type='video',
                    videoCategoryId='10',
                    maxResults=5
                ).execute()
                
                if search_response['items']:
                    # Analyze top performing videos
                    video_ids = [item['id']['videoId'] for item in search_response['items']]
                    videos_response = youtube.videos().list(
                        part='statistics',
                        id=','.join(video_ids)
                    ).execute()
                    
                    avg_views = calculate_avg_views(videos_response['items'])
                    competition = analyze_competition(videos_response['items'])
                    
                    keyword_stats[keyword] = {
                        'score': calculate_keyword_score(avg_views, competition),
                        'competition': competition,
                        'monthly_searches': estimate_searches(avg_views),
                        'avg_views': avg_views
                    }
                
                time.sleep(0.1)
                
            except Exception as e:
                if "quota" in str(e):
                    # Use cached data if available
                    if cached_data:
                        return cached_data
                    # Fallback data if no cache
                    keyword_stats[keyword] = {
                        'score': 0.5,
                        'competition': "Medium",
                        'monthly_searches': "1K-10K"
                    }
        
        # Save results to cache
        save_to_cache(cache_key, keyword_stats)
        return keyword_stats
        
    except Exception as e:
        st.warning("Using cached or estimated data due to API limitations")
        return get_fallback_data(genre)

def get_fallback_data(genre: str) -> Dict:
    """Provide fallback data when API is unavailable"""
    return {
        f"{genre}": {
            'score': 0.7,
            'competition': "Medium",
            'monthly_searches': "1K-10K"
        },
        f"new {genre} 2024": {
            'score': 0.8,
            'competition': "Low",
            'monthly_searches': "100-1K"
        }
    }

def calculate_avg_views(videos: List[Dict]) -> int:
    """Calculate average views of top videos"""
    views = [int(v['statistics'].get('viewCount', 0)) for v in videos]
    return sum(views) // len(views) if views else 0

def analyze_competition(videos: List[Dict]) -> str:
    """Analyze keyword competition level"""
    avg_views = calculate_avg_views(videos)
    if avg_views > 1000000:
        return "High"
    elif avg_views > 100000:
        return "Medium"
    return "Low"

def calculate_keyword_score(avg_views: int, competition: str) -> float:
    """Calculate keyword potential score"""
    base_score = min(avg_views / 1000000, 1.0) * 100
    competition_multiplier = {
        "Low": 1.2,
        "Medium": 1.0,
        "High": 0.8
    }
    return base_score * competition_multiplier[competition]

def estimate_searches(avg_views: int) -> str:
    """Estimate monthly searches based on views"""
    if avg_views > 1000000:
        return "100K+"
    elif avg_views > 100000:
        return "10K-100K"
    elif avg_views > 10000:
        return "1K-10K"
    return "100-1K"

def sort_keywords(keyword_stats: Dict) -> Dict:
    """Sort keywords by score"""
    return dict(sorted(
        keyword_stats.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    ))

def analyze_keyword_realtime(keyword: str) -> Optional[Dict]:
    """Analyze a single keyword in real-time"""
    try:
        # Check cache first
        cache_key = f"realtime_{keyword}"
        cached_data = get_cached_data(cache_key)
        if cached_data:
            return cached_data

        youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
        
        # Search for videos with this keyword
        search_response = youtube.search().list(
            q=keyword,
            part='snippet',
            type='video',
            videoCategoryId='10',  # Music category
            maxResults=5,
            regionCode='US'
        ).execute()
        
        total_results = search_response['pageInfo']['totalResults']
        
        # Get video statistics
        video_ids = [item['id']['videoId'] for item in search_response['items']]
        if video_ids:
            videos_response = youtube.videos().list(
                part='statistics',
                id=','.join(video_ids)
            ).execute()
            
            # Calculate average views and engagement
            views = []
            likes = []
            for video in videos_response['items']:
                stats = video['statistics']
                views.append(int(stats.get('viewCount', 0)))
                likes.append(int(stats.get('likeCount', 0)))
            
            avg_views = sum(views) / len(views) if views else 0
            engagement = sum(likes) / sum(views) if sum(views) > 0 else 0
            
            # Calculate keyword metrics
            score = calculate_keyword_score(avg_views, total_results, engagement)
            competition = get_competition_level(total_results)
            monthly_searches = estimate_monthly_searches(total_results)
            
            result = {
                'score': score,
                'competition': competition,
                'monthly_searches': monthly_searches,
                'avg_views': int(avg_views),
                'engagement_rate': f"{engagement*100:.1f}%"
            }
            
            # Cache the result
            save_to_cache(cache_key, result)
            return result
            
    except Exception as e:
        st.error(f"Real-time keyword analysis error: {str(e)}")
        return None

def calculate_keyword_score(avg_views: float, total_results: int, engagement: float) -> float:
    """Calculate keyword potential score (0-100)"""
    view_score = min(avg_views / 100000, 1.0) * 40  # 40% weight
    competition_score = (1 - min(total_results / 10000, 1.0)) * 30  # 30% weight
    engagement_score = min(engagement * 100, 1.0) * 30  # 30% weight
    
    return view_score + competition_score + engagement_score
