from typing import Dict, List

def generate_seo_tags(genre: str, track_name: str = "") -> Dict[str, List[str]]:
    """Generate SEO optimized tags and recommendations"""
    
    genre_keywords = {
        "Future House": [
            "future house",
            "edm",
            "electronic music",
            "dance music",
            "house music 2024"
        ]
    }
    
    title_templates = [
        f"{track_name} | {genre} Music",
        f"{genre} - {track_name}",
        f"New {genre} 2024 - {track_name}"
    ] if track_name else [
        f"New {genre} Track 2024",
        f"{genre} Music",
        f"Original {genre}"
    ]
    
    return {
        "title_suggestions": title_templates,
        "keywords": genre_keywords.get(genre, ["edm", "electronic music"])
    }
