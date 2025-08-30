import streamlit as st
import requests
import base64
from io import BytesIO
import time

# Page configuration
st.set_page_config(
    page_title="EchoVerse - AI Audiobook Creator",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for glassmorphism effect
def local_css():
    st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
        background-size: cover;
    }
    
    .glass {
        background: rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.18);
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.37);
        padding: 20px;
        margin-bottom: 20px;
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        border-radius: 15px;
        padding: 10px 24px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.2);
    }
    
    h1, h2, h3 {
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: rgba(0,0,0,0.5);
        color: white;
        text-align: center;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

local_css()

# App title and description
st.title("🎧 EchoVerse")
st.markdown("<h3 style='text-align: center; color: white;'>Transform Your Text into Expressive Audiobooks</h3>", 
            unsafe_allow_html=True)

# Initialize session state
if 'audio_url' not in st.session_state:
    st.session_state.audio_url = None
if 'rewritten_text' not in st.session_state:
    st.session_state.rewritten_text = None
if 'original_text' not in st.session_state:
    st.session_state.original_text = None

# Sidebar for settings
with st.sidebar:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.header("Settings")
    
    tone = st.selectbox(
        "Select Narration Tone",
        ("Neutral", "Suspenseful", "Inspiring"),
        help="Choose the emotional tone for your audiobook"
    )
    
    voice = st.selectbox(
        "Select Voice",
        ("en-US_AllisonV3Voice", "en-US_LisaV3Voice", "en-US_MichaelV3Voice"),
        help="Choose the voice for narration"
    )
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.header("About EchoVerse")
    st.info("""
    EchoVerse uses IBM Watson AI to transform your text into expressive audiobooks. 
    Just paste your text, select your preferred tone and voice, and let AI do the rest!
    """)
    st.markdown("</div>", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Input Text")
    
    input_method = st.radio(
        "Choose input method:",
        ("Paste text", "Upload file")
    )
    
    text_input = ""
    
    if input_method == "Paste text":
        text_input = st.text_area(
            "Paste your text here:",
            height=300,
            placeholder="Once upon a time...",
            help="Paste the text you want to convert to audiobook"
        )
    else:
        uploaded_file = st.file_uploader(
            "Upload a text file",
            type=['txt'],
            help="Upload a .txt file with your content"
        )
        if uploaded_file is not None:
            text_input = uploaded_file.read().decode("utf-8")
            st.text_area("File content:", value=text_input, height=300)
    
    process_btn = st.button("Generate Audiobook", use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='glass'>", unsafe_allow_html=True)
    st.subheader("Output")
    
    if process_btn and text_input:
        with st.spinner("Generating your audiobook... This may take a moment."):
            # Simulate API call to backend
            try:
                # In a real implementation, this would call your Flask backend
                # For demo purposes, we'll simulate the response
                time.sleep(2)  # Simulate processing time
                
                # Simulate tone adaptation
                if tone == "Suspenseful":
                    rewritten_text = text_input + ".. with bated breath, wondering what would happen next."
                elif tone == "Inspiring":
                    rewritten_text = text_input + " And remember, the greatest journeys begin with a single step."
                else:
                    rewritten_text = text_input
                
                # Store in session state
                st.session_state.original_text = text_input
                st.session_state.rewritten_text = rewritten_text
                st.session_state.audio_url = "https://example.com/audio/sample.mp3"  # Simulated URL
                
            except Exception as e:
                st.error(f"Error generating audiobook: {str(e)}")
    
    if st.session_state.rewritten_text:
        st.success("Audiobook generated successfully!")
        
        # Display original and rewritten text comparison
        st.subheader("Text Comparison")
        tab1, tab2 = st.tabs(["Original Text", "Adapted Text"])
        
        with tab1:
            st.text_area("Original", value=st.session_state.original_text, height=150)
        
        with tab2:
            st.text_area("Adapted", value=st.session_state.rewritten_text, height=150)
        
        # Audio player and download
        st.subheader("Generated Audio")
        
        # In a real implementation, this would play the actual generated audio
        # For demo, we'll use a placeholder
        st.audio("https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3", format="audio/mp3")
        
        # Download button
        st.download_button(
            label="Download Audio",
            data="Simulated audio data",  # In real implementation, this would be the audio bytes
            file_name="echoverse_audiobook.mp3",
            mime="audio/mpeg",
            use_container_width=True
        )
    else:
        st.info("Your generated audiobook will appear here. Paste some text and click 'Generate Audiobook' to get started.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: white;'>"
    "EchoVerse - Built with IBM Watson AI for the CognitiveX Hackathon 2025"
    "</div>", 
    unsafe_allow_html=True
)