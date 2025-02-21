from typing import Dict, List

def generate_seo_tags(genre: str, track_name: str = "") -> Dict[str, List[str]]:
    """Generate SEO optimized tags and recommendations"""
    
    genre_keywords = {
        "Future House": [
            "future house music",
            "electronic dance music",
            "EDM",
            "house music",
            "dance music 2024",
            "future house mix",
            "oliver heldens style",
            "don diablo type"
        ],
        "Tech House": [
            "tech house",
            "underground house",
            "club music",
            "tech house beats",
            "fisher style",
            "solardo type",
            "groove house"
        ],
        "Bass House": [
            "bass house",
            "jauz style",
            "joyryde type",
            "ac slater",
            "night bass",
            "heavy bass music"
        ]
    }
    
    title_templates = [
        f"{track_name} | {genre} Music",
        f"{genre} - {track_name} [Free Download]",
        f"New {genre} 2024 - {track_name}"
    ]
    
    description_template = f"""
🎵 {track_name}
Genre: {genre}

Free Download: [Your Link]

Follow me:
▶ Instagram: 
▶ SoundCloud: 
▶ YouTube: 

#edm #{genre.replace(' ', '')} #music
    """
    
    return {
        "keywords": genre_keywords.get(genre, ["EDM", "electronic music"]),
        "title_suggestions": title_templates,
        "description": description_template,
        "best_upload_times": [
            "Saturday 2-4 PM EST",
            "Sunday 1-3 PM EST",
            "Thursday 7-9 PM EST"
        ],
        "thumbnail_tips": [
            "Use high contrast colors",
            "Include genre name",
            "Add artist name",
            "Use modern EDM-style fonts"
        ]
    }
