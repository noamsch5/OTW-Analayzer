import streamlit as st
import os
import logging
from src.api.youtube import find_similar_tracks
from src.api.youtube_seo import generate_seo_tags
from src.audio.analyzer import analyze_audio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_audio_file(file):
    """Process uploaded audio file and extract features"""
    try:
        logger.info(f"Processing file: {file.name}")
        # Save temporary file
        with open("temp.wav", "wb") as f:
            f.write(file.getbuffer())
        
        # Analyze audio
        audio_features = analyze_audio("temp.wav")
        
        # Combine with file info
        track_features = {
            "name": file.name.replace(".wav", ""),
            **audio_features
        }
        
        logger.info(f"Audio analysis complete: {track_features}")
        return track_features
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise
    finally:
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

def main():
    st.set_page_config(page_title="OTW Analayzer", page_icon="🎵", layout="wide")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🎵 OTW Analayzer")
        st.subheader("EDM Track Analysis & YouTube Optimization")
        
        uploaded_file = st.file_uploader("Drop your track here", type=['wav'])
        
        if uploaded_file:
            with st.spinner("Analyzing track..."):
                track_features = process_audio_file(uploaded_file)
                genre = track_features["genre"]
                
                # Create tabs for different analyses
                tab1, tab2, tab3 = st.tabs(["Analysis", "Similar Tracks", "YouTube SEO"])
                
                with tab1:
                    st.success("Analysis complete!")
                    col3, col4 = st.columns(2)
                    with col3:
                        st.metric("Genre", genre)
                        st.metric("Key", track_features["key"])
                    with col4:
                        st.metric("BPM", track_features["bpm"])
                        st.metric("Energy", track_features["energy"])
                
                with tab2:
                    similar_tracks = find_similar_tracks(genre, track_features)
                    for track in similar_tracks:
                        with st.container():
                            col5, col6 = st.columns([1, 3])
                            with col5:
                                st.image(track['thumbnail'])
                            with col6:
                                st.markdown(f"#### [{track['title']}]({track['url']})")
                                st.caption(f"Channel: {track['channel']}")
                
                with tab3:
                    seo_data = generate_seo_tags(genre, track_features)
                    
                    st.subheader("📈 YouTube Optimization")
                    
                    st.write("### 🎯 Title Suggestions")
                    for title in seo_data["title_suggestions"]:
                        st.info(title)
                    
                    st.write("### 🔑 Keywords")
                    st.code(", ".join(seo_data["keywords"]))
                    
                    st.write("### 📝 Description Template")
                    st.text_area("Copy this description:", value=seo_data["description"], height=300)
                    
                    col7, col8 = st.columns(2)
                    with col7:
                        st.write("### ⏰ Best Upload Times")
                        for time in seo_data["upload_times"]:
                            st.write(f"• {time}")
                    with col8:
                        st.write("### 🖼️ Thumbnail Tips")
                        for tip in seo_data["thumbnail_tips"]:
                            st.write(f"• {tip}")
    
    with col2:
        st.info("💡 Pro tip: Use high-quality WAV files for best results")
        st.info("✨ Upload during recommended times for better reach")

    st.markdown("---")
    st.markdown("Made with ❤️ for EDM producers")

if __name__ == "__main__":
    main()
