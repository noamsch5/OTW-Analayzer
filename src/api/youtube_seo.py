from typing import Dict, List

def generate_seo_tags(genre: str) -> Dict[str, List[str]]:
    """Generate basic SEO tags"""
    return {
        "keywords": ["edm", "electronic music"],
        "title_suggestions": [f"New {genre} Track 2024"]
    }
