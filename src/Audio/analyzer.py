import librosa
import numpy as np
import logging

logger = logging.getLogger(__name__)

def analyze_audio(file_path: str) -> dict:
    """Analyze audio file and extract features"""
    try:
        # Load audio with higher sample rate
        y, sr = librosa.load(file_path, duration=60, sr=44100)
        logger.info("Audio file loaded successfully")

        # Improved BPM detection using multiple methods
        onset_env = librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median)
        tempo_candidates = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, aggregate=None)
        
        # Get the most prominent tempo
        tempo = float(librosa.beat.tempo(onset_envelope=onset_env, sr=sr))
        
        # Refine BPM to common EDM ranges (115-135 BPM)
        if tempo < 115:
            tempo *= 2
        elif tempo > 135:
            tempo /= 2
            
        # Enhanced key detection using multiple features
        y_harmonic = librosa.effects.harmonic(y)
        chromagram = librosa.feature.chroma_stft(y=y_harmonic, sr=sr, n_chroma=12)
        chroma_vals = np.mean(chromagram, axis=1)
        
        # Key detection with confidence check
        key_idx = np.argmax(chroma_vals)
        key_confidence = chroma_vals[key_idx] / np.sum(chroma_vals)
        
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Improved major/minor detection
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        major_profile = np.roll(major_profile, key_idx)
        minor_profile = np.roll(minor_profile, key_idx)
        
        major_corr = np.corrcoef(chroma_vals, major_profile)[0,1]
        minor_corr = np.corrcoef(chroma_vals, minor_profile)[0,1]
        
        key_quality = "Major" if major_corr > minor_corr else "Minor"
        
        return {
            "bpm": str(int(round(tempo))),
            "key": f"{keys[key_idx]} {key_quality}",
            "key_confidence": f"{key_confidence:.2%}",
            "energy": calculate_energy(y),
            "genre": detect_genre(tempo, y, sr)
        }
        
    except Exception as e:
        logger.error(f"Error in audio analysis: {str(e)}")
        raise

def calculate_energy(y: np.ndarray) -> str:
    """Calculate track energy using multiple features"""
    rms = librosa.feature.rms(y=y)[0]
    spectral = librosa.feature.spectral_centroid(y=y)[0]
    
    energy_score = (np.mean(rms) * 0.6 + np.percentile(spectral, 95) / 10000 * 0.4)
    
    if energy_score > 0.15:
        return "High"
    elif energy_score > 0.08:
        return "Medium"
    return "Low"

def detect_genre(tempo: float, y: np.ndarray, sr: int) -> str:
    """Detect EDM subgenre based on audio features"""
    spectral = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    spectral_mean = np.mean(spectral)
    
    if 124 <= tempo <= 128:
        if calculate_energy(y) == "High" and spectral_mean > 2000:
            return "Future House"
        return "Tech House"
    elif 128 <= tempo <= 135 and calculate_energy(y) == "High":
        return "Bass House"
    elif 126 <= tempo <= 130:
        return "Progressive House"
    return "House"
