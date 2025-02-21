import streamlit as st
import os
import logging
from src.api.youtube import find_similar_tracks

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def process_audio_file(file):
    """Process uploaded audio file and return genre"""
    try:
        logger.info(f"Processing file: {file.name}")
        # Save temporary file
        with open("temp.wav", "wb") as f:
            f.write(file.getbuffer())
        logger.info("Audio file saved successfully")
        return "Future House"  # Placeholder genre
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        raise
    finally:
        if os.path.exists("temp.wav"):
            os.remove("temp.wav")
            logger.info("Temporary file cleaned up")

def main():
    # Page configuration
    st.set_page_config(
        page_title="OTW Analayzer",
        page_icon="🎵",
        layout="wide"
    )
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/nolan/64/musical-notes.png")
        st.markdown("""
        ## How to use
        1. Upload your EDM track (WAV)
        2. Get instant genre analysis
        3. Find similar tracks
        4. Get optimization tips
        """)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.title("🎵 OTW Analayzer")
        st.subheader("EDM Track Analysis & YouTube Optimization")
        
        uploaded_file = st.file_uploader(
            "Drop your track here",
            type=['wav'],
            help="Supported format: WAV"
        )
        
        if uploaded_file:
            try:
                with st.spinner("Processing audio..."):
                    genre = process_audio_file(uploaded_file)
                    
                    # Create tabs for results
                    tab1, tab2 = st.tabs(["Analysis", "Similar Tracks"])
                    
                    with tab1:
                        st.success("Analysis complete!")
                        col3, col4 = st.columns(2)
                        with col3:
                            st.metric("Genre", genre)
                        with col4:
                            st.metric("BPM", "128")
                    
                    with tab2:
                        similar_tracks = find_similar_tracks(genre)
                        for track in similar_tracks[:5]:
                            with st.container():
                                st.write(f"#### {track['title']}")
                                st.caption(f"Channel: {track['channel']}")
                                st.divider()
            
            except Exception as e:
                st.error("Error processing file. Please try again.")
                logger.error(f"Error: {str(e)}")
    
    with col2:
        st.info("💡 Pro tip: Use high-quality WAV files for best results")
        st.info("✨ Coming soon: Extended genre detection!")

    # Footer
    st.markdown("---")
    st.markdown("Made with ❤️ for EDM producers")

if __name__ == "__main__":
    main()
