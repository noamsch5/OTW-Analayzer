from typing import Dict, List

def generate_seo_tags(genre: str, track_name: str = "") -> Dict[str, List[str]]:
    """Generate SEO optimized tags and recommendations"""
    
    genre_keywords = {
        "Future House": [
            "future house music",
            "edm",
            "electronic music",
            "dance music 2024"
        ]
    }
    
    title_templates = [
        f"New {genre} Track 2024",
        f"{genre} Music Mix"
    ]
    
    return {
        "title_suggestions": title_templates,
        "keywords": genre_keywords.get(genre, ["edm", "electronic music"])
    }
