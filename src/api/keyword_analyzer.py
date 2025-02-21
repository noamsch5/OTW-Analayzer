from googleapiclient.discovery import build
import streamlit as st
from typing import Dict, List
import time

def analyze_keywords(genre: str, track_features: Dict) -> Dict[str, List]:
    """Analyze keywords and their rankings"""
    try:
        youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
        
        # Generate keyword combinations
        base_keywords = [
            f"{genre} music",
            f"{genre} {track_features['bpm']}bpm",
            f"{genre} {track_features['key']}",
            f"new {genre} 2024",
            f"{genre} type beat",
            f"{genre} mix"
        ]
        
        keyword_stats = {}
        for keyword in base_keywords:
            search_response = youtube.search().list(
                q=keyword,
                part='snippet',
                type='video',
                maxResults=5,
                videoCategoryId='10'  # Music category
            ).execute()
            
            # Calculate ranking score based on view counts and competition
            video_count = search_response['pageInfo']['totalResults']
            ranking_score = calculate_ranking_score(video_count)
            
            keyword_stats[keyword] = {
                'score': ranking_score,
                'competition': get_competition_level(video_count),
                'monthly_searches': estimate_monthly_searches(video_count)
            }
            
            time.sleep(0.5)  # Respect API limits
        
        return sort_keywords_by_potential(keyword_stats)
        
    except Exception as e:
        st.error(f"Keyword analysis error: {str(e)}")
        return {}

def calculate_ranking_score(video_count: int) -> float:
    """Calculate keyword ranking score"""
    if video_count < 1000:
        return 0.9  # Low competition, high potential
    elif video_count < 10000:
        return 0.7  # Medium competition
    else:
        return 0.5  # High competition

def get_competition_level(video_count: int) -> str:
    """Determine keyword competition level"""
    if video_count < 1000:
        return "Low"
    elif video_count < 10000:
        return "Medium"
    else:
        return "High"

def estimate_monthly_searches(video_count: int) -> str:
    """Estimate monthly search volume"""
    if video_count < 1000:
        return "100-1K"
    elif video_count < 10000:
        return "1K-10K"
    else:
        return "10K+"

def sort_keywords_by_potential(keyword_stats: Dict) -> Dict:
    """Sort keywords by potential ranking"""
    sorted_keywords = sorted(
        keyword_stats.items(),
        key=lambda x: x[1]['score'],
        reverse=True
    )
    return dict(sorted_keywords)
