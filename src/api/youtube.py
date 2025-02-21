from googleapiclient.discovery import build
import os
import logging
from typing import List, Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_similar_tracks(genre: str) -> List[Dict]:
    """Find similar tracks on YouTube based on genre"""
    try:
        api_key = os.getenv('YOUTUBE_API_KEY')
        if not api_key:
            logger.error("YouTube API key not found")
            return []
            
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        search_response = youtube.search().list(
            q=f"{genre} music",
            part='snippet',
            maxResults=5,
            type='video'
        ).execute()
        
        return [{
            'title': item['snippet']['title'],
            'channel': item['snippet']['channelTitle'],
            'videoId': item['id']['videoId']
        } for item in search_response.get('items', [])]
        
    except Exception as e:
        logger.error(f"Error in YouTube API: {str(e)}")
        return []
