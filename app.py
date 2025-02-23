import streamlit as st
import os
import logging
from src.api.youtube import find_similar_tracks, analyze_keyword_realtime, get_youtube_client
from src.api.youtube_seo import generate_seo_tags
from src.api.keyword_analyzer import analyze_keywords, get_fallback_data
from src.Audio.analyzer import analyze_audio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Check for API keys
if not st.secrets.get("YOUTUBE_API_KEY") and not st.secrets.get("YOUTUBE_API_KEYS"):
    st.error("YouTube API key not found. Please add it to your .streamlit/secrets.toml file")

def process_audio_file(file):
    """Process uploaded audio file and extract features"""
    try:
        logger.info(f"Processing file: {file.name}")
        # Save temporary file
        with open("temp.wav", "wb") as f:
            f.write(file.getbuffer())
        
        # Analyze audio with error handling
        try:
            audio_features = analyze_audio("temp.wav")
            logger.info("Audio analysis completed successfully")
        except Exception as e:
            logger.error(f"Audio analysis failed: {str(e)}")
            st.warning("Audio analysis encountered issues. Using default values.")
            audio_features = {
                "bpm": "128",
                "key": "C Major",
                "energy": "Medium",
                "genre": "House"
            }
        
        # Combine with file info
        track_features = {
            "name": file.name.replace(".wav", ""),
            **audio_features
        }
        
        return track_features
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        st.error("Error processing file. Please try again.")
        return None
    finally:
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")

def main():
    st.set_page_config(page_title="OTW Analyzer", page_icon="🎵", layout="wide")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🎵 OTW Analyzer")
        st.subheader("EDM Track Analysis & YouTube Optimization")
        
        uploaded_file = st.file_uploader("Drop your track here", type=['wav'])
        
        if uploaded_file:
            track_features = process_audio_file(uploaded_file)
            
            if track_features:
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
                    try:
                        similar_tracks = find_similar_tracks(genre, track_features)
                        if similar_tracks:
                            for track in similar_tracks:
                                with st.container():
                                    col5, col6 = st.columns([1, 3])
                                    with col5:
                                        if 'thumbnail' in track:
                                            st.image(track['thumbnail'])
                                    with col6:
                                        st.markdown(f"#### [{track['title']}]({track['url']})")
                                        st.caption(f"Channel: {track['channel']}")
                                        if 'views' in track and 'likes' in track:
                                            st.caption(f"👀 {track['views']:,} views | 👍 {track['likes']:,} likes")
                        else:
                            st.info("Similar tracks will appear here when API quota is available")
                    except Exception as e:
                        st.warning("Could not fetch similar tracks. Try again later.")
                        logger.error(f"Error fetching similar tracks: {str(e)}")
                
                with tab3:
                    seo_data = generate_seo_tags(genre, track_features)
                    st.write("### 🎯 Title Suggestions")
                    for title in seo_data["title_suggestions"]:
                        st.info(title)
                    
                    # Add real-time keyword analyzer
                    st.write("### 🔍 Analyze Custom Keywords")
                    custom_keyword = st.text_input("Enter keyword to analyze:", 
                                                help="Type a keyword and see real-time metrics")
                    
                    if custom_keyword:
                        try:
                            keyword_metrics = analyze_keyword_realtime(custom_keyword)
                            if keyword_metrics:
                                col7, col8, col9 = st.columns(3)
                                with col7:
                                    score = keyword_metrics.get('score', 0)
                                    score_color = "green" if score > 70 else "orange" if score > 40 else "red"
                                    st.markdown(f"Score: <span style='color:{score_color}'>{score:.1f}</span>", 
                                            unsafe_allow_html=True)
                                with col8:
                                    st.write(f"Competition: {keyword_metrics.get('competition', 'Unknown')}")
                                with col9:
                                    st.write(f"Monthly Searches: {keyword_metrics.get('monthly_searches', 'Unknown')}")
                        except Exception as e:
                            st.info("Keyword analysis temporarily unavailable. Try again later.")
                            logger.error(f"Keyword analysis error: {str(e)}")
    
    with col2:
        st.info("💡 Pro tip: Use high-quality WAV files for best results")
        st.info("✨ Upload during recommended times for better reach")

    st.markdown("---")
    st.markdown("Made with ❤️ for EDM producers")

if __name__ == "__main__":
    main()
