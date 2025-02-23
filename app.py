import streamlit as st
import os
import logging
from src.api.youtube import find_similar_tracks, analyze_keyword_realtime, get_youtube_client
from src.api.youtube_seo import generate_seo_tags
from src.api.keyword_analyzer import analyze_keywords, get_fallback_data
from src.Audio.analyzer import analyze_audio

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
                
                # Add API quota warning
                st.info("Note: Some features might use cached data due to API limitations")
                
                # Analyze keywords with quota handling
                with st.spinner("Analyzing YouTube keywords..."):
                    try:
                        keyword_data = analyze_keywords(genre, track_features)
                    except Exception as e:
                        st.warning("Using cached keyword data due to API limitations")
                        keyword_data = get_fallback_data(genre)
                
                # Create tabs for different analyses
                tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Similar Tracks", "YouTube SEO", "Keyword Rankings"])
                
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
                                st.caption(f"👀 {track['views']:,} views | 👍 {track['likes']:,} likes")
                
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
                    
                    # Add real-time keyword analyzer
                    st.write("### 🔍 Analyze Custom Keywords")
                    custom_keyword = st.text_input("Enter keyword to analyze:", 
                                                 help="Type a keyword and see real-time metrics")
                    
                    if custom_keyword:
                        with st.spinner("Analyzing keyword..."):
                            keyword_metrics = analyze_keyword_realtime(custom_keyword)
                            
                            if keyword_metrics:
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    score_color = "green" if keyword_metrics['score'] > 70 else "orange" if keyword_metrics['score'] > 40 else "red"
                                    st.markdown(f"Score: <span style='color:{score_color}'>{keyword_metrics['score']:.1f}</span>", 
                                              unsafe_allow_html=True)
                                with col2:
                                    st.write(f"Competition: {keyword_metrics['competition']}")
                                with col3:
                                    st.write(f"Monthly Searches: {keyword_metrics['monthly_searches']}")
                
                with tab4:
                    st.subheader("🎯 Keyword Analysis")
                    
                    # Display keyword rankings
                    for keyword, stats in keyword_data.items():
                        with st.container():
                            col9, col10, col11 = st.columns([3, 1, 1])
                            with col9:
                                st.markdown(f"### `{keyword}`")
                            with col10:
                                score_color = "green" if stats['score'] > 0.7 else "orange" if stats['score'] > 0.5 else "red"
                                st.markdown(f"Score: <span style='color:{score_color}'>{stats['score']:.2f}</span>", unsafe_allow_html=True)
                            with col11:
                                competition_color = "green" if stats['competition'] == "Low" else "orange" if stats['competition'] == "Medium" else "red"
                                st.markdown(f"Competition: <span style='color:{competition_color}'>{stats['competition']}</span>", unsafe_allow_html=True)
                            st.caption(f"Monthly Searches: {stats['monthly_searches']}")
                            st.divider()
    
    with col2:
        st.info("💡 Pro tip: Use high-quality WAV files for best results")
        st.info("✨ Upload during recommended times for better reach")
        st.info("🎯 Focus on keywords with high scores and low competition")

    st.markdown("---")
    st.markdown("Made with ❤️ for EDM producers")

if __name__ == "__main__":
    main()
