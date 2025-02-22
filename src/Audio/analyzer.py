import librosa
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_audio(file_path: str) -> dict:
    """Analyze audio file and extract features"""
    try:
        # Load audio with larger duration for better analysis
        y, sr = librosa.load(file_path, duration=120)  # Analyze first 2 minutes
        logger.info("Audio file loaded successfully")

        # Enhanced BPM detection
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        tempo_raw = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)
        
        # Refine BPM to common EDM ranges
        tempo = round(tempo_raw[0])
        if tempo < 100:
            tempo *= 2
        elif tempo > 160:
            tempo //= 2
            
        # Enhanced key detection
        y_harmonic = librosa.effects.harmonic(y)
        chromagram = librosa.feature.chroma_cqt(y=y_harmonic, sr=sr)
        
        # Key detection using chromagram
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        chroma_avg = np.mean(chromagram, axis=1)
        key_idx = np.argmax(chroma_avg)
        
        # Determine if major or minor
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        
        # Rotate profiles to match detected key
        major_profile = np.roll(major_profile, key_idx)
        minor_profile = np.roll(minor_profile, key_idx)
        
        # Calculate correlation
        major_corr = np.correlate(chroma_avg, major_profile)
        minor_corr = np.correlate(chroma_avg, minor_profile)
        
        # Determine key quality
        key_quality = "Major" if major_corr > minor_corr else "Minor"
        
        # Calculate energy
        rms = librosa.feature.rms(y=y)[0]
        spectral = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        energy_level = calculate_energy(rms, spectral)
        
        # Determine genre based on features
        genre = detect_genre(tempo, energy_level, spectral)
        
        return {
            "bpm": str(int(tempo)),
            "key": f"{keys[key_idx]} {key_quality}",
            "energy": energy_level,
            "genre": genre
        }
        
    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        raise

def calculate_energy(rms: np.ndarray, spectral: np.ndarray) -> str:
    """Calculate track energy level"""
    rms_mean = np.mean(rms)
    spectral_mean = np.mean(spectral)
    
    if rms_mean > 0.1 and spectral_mean > 2000:
        return "High"
    elif rms_mean > 0.05:
        return "Medium"
    return "Low"

def detect_genre(tempo: float, energy: str, spectral: np.ndarray) -> str:
    """Detect EDM subgenre based on audio features"""
    spectral_mean = np.mean(spectral)
    
    if 124 <= tempo <= 128:
        if energy == "High" and spectral_mean > 2000:
            return "Future House"
        return "Tech House"
    elif 128 <= tempo <= 135 and energy == "High":
        return "Bass House"
    elif 126 <= tempo <= 130:
        return "Progressive House"
    return "House"
