import librosa
import numpy as np

def analyze_audio(file_path: str) -> dict:
    """Analyze audio file and extract features"""
    try:
        # Load audio file
        y, sr = librosa.load(file_path)
        
        # Extract features
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        chroma = librosa.feature.chroma_stft(y=y, sr=sr)
        spectral = librosa.feature.spectral_centroid(y=y, sr=sr)
        
        # Determine key
        chroma_avg = np.mean(chroma, axis=1)
        key_idx = np.argmax(chroma_avg)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        key = keys[key_idx]
        
        # Calculate energy
        energy = np.mean(librosa.feature.rms(y=y))
        energy_level = "High" if energy > 0.1 else "Medium" if energy > 0.05 else "Low"
        
        # Determine genre based on features
        genre = determine_genre(tempo, energy, spectral)
        
        return {
            "bpm": str(int(round(tempo))),
            "key": f"{key} Minor" if is_minor(chroma) else f"{key} Major",
            "energy": energy_level,
            "genre": genre
        }
    except Exception as e:
        raise Exception(f"Error analyzing audio: {str(e)}")

def determine_genre(tempo: float, energy: float, spectral) -> str:
    """Determine genre based on audio features"""
    genres = {
        "Future House": (tempo >= 125 and tempo <= 130 and energy > 0.08),
        "Tech House": (tempo >= 120 and tempo <= 127 and energy > 0.07),
        "Bass House": (tempo >= 126 and tempo <= 132 and np.mean(spectral) > 2000),
        "Deep House": (tempo >= 120 and tempo <= 125 and energy <= 0.07),
        "Progressive House": (tempo >= 126 and tempo <= 130 and energy > 0.06),
    }
    
    return next((genre for genre, condition in genres.items() if condition), "EDM")

def is_minor(chroma) -> bool:
    """Determine if the key is minor"""
    minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
    major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
    
    chroma_sum = np.sum(chroma, axis=1)
    minor_corr = np.correlate(chroma_sum, minor_profile)
    major_corr = np.correlate(chroma_sum, major_profile)
    
    return minor_corr > major_corr
