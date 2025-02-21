from typing import Dict, List

def generate_seo_tags(genre: str, track_features: Dict = None) -> Dict:
    """Generate SEO tags based on genre and track features"""
    
    genre_keywords = {
        "Future House": [
            "future house music",
            "future bounce",
            "oliver heldens style",
            "don diablo type beat",
            f"future house {track_features.get('bpm', '128')}bpm" if track_features else "future house",
            "electronic dance music",
            "edm 2024"
        ],
        "Tech House": [
            "tech house",
            "underground house",
            "tech house groove",
            "fisher style",
            "club music 2024",
            f"tech house {track_features.get('bpm', '125')}bpm" if track_features else "tech house"
        ],
        "Bass House": [
            "bass house",
            "jauz style",
            "bass heavy edm",
            "night bass",
            f"bass house {track_features.get('bpm', '128')}bpm" if track_features else "bass house"
        ]
    }
    
    title_templates = [
        f"{track_features.get('name', 'New Track')} | {genre} Music",
        f"{genre} - {track_features.get('name', 'Original Mix')} [{track_features.get('bpm', '128')}BPM]",
        f"New {genre} 2024 - {track_features.get('name', 'Original Mix')}"
    ]
    
    description_template = f"""
🎵 {track_features.get('name', 'New Track')}
Genre: {genre}
BPM: {track_features.get('bpm', '128')}
Key: {track_features.get('key', 'N/A')}

Free Download: [Your Link]

Track Info:
• Genre: {genre}
• Style: Electronic Dance Music
• BPM: {track_features.get('bpm', '128')}
• Key: {track_features.get('key', 'N/A')}

Follow me:
▶ Instagram: [Your Instagram]
▶ SoundCloud: [Your SoundCloud]
▶ YouTube: [Your Channel]

#edm #{genre.replace(' ', '').lower()} #music #producer #edmproducer
    """
    
    return {
        "title_suggestions": title_templates,
        "keywords": genre_keywords.get(genre, ["edm", "electronic music"]),
        "description": description_template,
        "upload_times": [
            "Saturday 2-4 PM EST",
            "Sunday 1-3 PM EST",
            "Thursday 7-9 PM EST"
        ],
        "thumbnail_tips": [
            "Use bright, contrasting colors",
            f"Include '{genre}' text",
            "Add your artist name",
            "Use EDM-style waveform graphics"
        ]
    }
