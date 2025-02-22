import librosa
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_audio(file_path: str) -> dict:
    """Analyze audio file and extract features"""
    try:
        # Load audio with error handling
        try:
            y, sr = librosa.load(file_path, duration=60)  # Limit to first 60 seconds
            logger.info("Audio file loaded successfully")
        except Exception as e:
            logger.error(f"Error loading audio: {str(e)}")
            return {
                "bpm": "128",
                "key": "C Major",
                "energy": "Medium",
                "genre": "House"
            }

        # Extract BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Extract key
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key_idx = np.argmax(np.mean(chroma, axis=1))
        
        # Calculate energy
        rms = librosa.feature.rms(y=y)[0]
        energy_level = "High" if np.mean(rms) > 0.1 else "Medium"
        
        # Determine genre
        genre = "House"  # Default genre
        if 124 <= tempo <= 128:
            if np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)) > 2000:
                genre = "Future House"
            else:
                genre = "Tech House"
        
        return {
            "bpm": str(int(round(tempo))),
            "key": f"{keys[key_idx]} Major",
            "energy": energy_level,
            "genre": genre
        }
        
    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        # Return default values if analysis fails
        return {
            "bpm": "128",
            "key": "C Major",
            "energy": "Medium",
            "genre": "House"
        }
