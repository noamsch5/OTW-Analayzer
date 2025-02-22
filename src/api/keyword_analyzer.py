from googleapiclient.discovery import build
import streamlit as st
from typing import Dict
import time

def analyze_keywords(genre: str, track_features: Dict) -> Dict:
    """Analyze and rank YouTube keywords"""
    try:
        youtube = build('youtube', 'v3', developerKey=st.secrets["YOUTUBE_API_KEY"])
        
        # Generate relevant keyword combinations
        base_keywords = [
            f"{genre}",
            f"{genre} music",
            f"{genre} {track_features['bpm']}bpm",
            f"{genre} {track_features['key']}",
            f"new {genre} 2024",
            f"{track_features['key']} {genre}",
            f"{genre} mix 2024",
            f"best {genre}",
            f"{genre} playlist"
        ]
        
        keyword_stats = {}
        
        for keyword in base_keywords:
            # Search for videos with keyword
            search_response = youtube.search().list(
                q=keyword,
                part='snippet',
                type='video',
                videoCategoryId='10',
                maxResults=5
            ).execute()
            
            # Analyze search results
            total_results = search_response['pageInfo']['totalResults']
            competition = get_competition_level(total_results)
            
            # Get view counts for top videos
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            if video_ids:
                videos_response = youtube.videos().list(
                    part='statistics',
                    id=','.join(video_ids)
                ).execute()
                
                avg_views = sum(
                    int(video['statistics'].get('viewCount', 0))
                    for video in videos_response['items']
                ) / len(videos_response['items'])
                
                keyword_stats[keyword] = {
                    'score': calculate_keyword_score(total_results, avg_views),
                    'competition': competition,
                    'monthly_searches': estimate_monthly_searches(total_results),
                    'avg_views': int(avg_views)
                }
            
            time.sleep(0.1)  # Respect API limits
        
        return {k: v for k, v in sorted(
            keyword_stats.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )}
        
    except Exception as e:
        st.error(f"Keyword analysis error: {str(e)}")
        return {}

def calculate_keyword_score(total_results: int, avg_views: float) -> float:
    """Calculate keyword potential score"""
    if total_results == 0:
        return 0
    
    competition_factor = 1.0 if total_results < 1000 else 0.7 if total_results < 10000 else 0.4
    view_factor = min(avg_views / 10000, 1.0)
    
    return (competition_factor * 0.6 + view_factor * 0.4) * 100

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
    return "10K+"
