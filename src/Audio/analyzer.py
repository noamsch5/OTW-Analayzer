import librosa
import numpy as np

def analyze_audio(file_path: str) -> dict:
    """Analyze audio features using librosa"""
    try:
        # Load audio file
        y, sr = librosa.load(file_path)
        
        # Extract BPM
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Extract key
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
        key_correlation = [
            sum(sum(librosa.segment.cross_similarity(chroma, librosa.feature.chroma_cqt(librosa.tone.note_to_hz([note]), sr=sr))))
            for note in ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        ]
        key_idx = np.argmax(key_correlation)
        keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        
        # Determine if major or minor
        minor_profile = np.array([1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 0])
        major_profile = np.array([1, 0, 1, 0, 1, 1, 0, 1, 0, 1, 0, 1])
        
        chroma_avg = np.mean(chroma, axis=1)
        minor_corr = np.correlate(chroma_avg, minor_profile)
        major_corr = np.correlate(chroma_avg, major_profile)
        
        key_quality = "Minor" if minor_corr > major_corr else "Major"
        
        return {
            "bpm": int(round(tempo)),
            "key": f"{keys[key_idx]} {key_quality}",
            "energy": calculate_energy(y),
            "genre": detect_genre(y, sr, tempo)
        }
    except Exception as e:
        raise Exception(f"Error in audio analysis: {str(e)}")

def calculate_energy(y) -> str:
    """Calculate track energy level"""
    rms = librosa.feature.rms(y=y)[0]
    mean_energy = np.mean(rms)
    if mean_energy > 0.1:
        return "High"
    elif mean_energy > 0.05:
        return "Medium"
    return "Low"

def detect_genre(y, sr, tempo) -> str:
    """Detect EDM subgenre based on audio features"""
    # Extract features for genre detection
    spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
    spectral_rolloff = np.mean(librosa.feature.spectral_rolloff(y=y, sr=sr))
    onset_env = librosa.onset.onset_strength(y=y, sr=sr)
    onset_tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr)[0]
    
    # Genre classification logic
    if 125 <= tempo <= 130 and spectral_centroid > 2000:
        return "Future House"
    elif 120 <= tempo <= 125 and spectral_rolloff < 3000:
        return "Deep House"
    elif 124 <= tempo <= 128 and spectral_centroid > 3000:
        return "Tech House"
    elif 128 <= tempo <= 135 and spectral_centroid > 4000:
        return "Bass House"
    elif 126 <= tempo <= 130 and onset_tempo > 120:
        return "Progressive House"
    return "House"
