from googleapiclient.discovery import build
import streamlit as st
from typing import Dict, List
import time

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

def analyze_keywords(genre: str, track_features: Dict) -> Dict:
    """Analyze successful EDM track keywords"""
    try:
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
            # Search for successful tracks
            search_response = youtube.search().list(
                q=keyword,
                part='snippet',
                type='video',
                videoCategoryId='10',
                maxResults=5,
                order='viewCount'
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
        
        return sort_keywords(keyword_stats)
        
    except Exception as e:
        st.error(f"Keyword analysis error: {str(e)}")
        return {}

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
