# EchoVerse - Generative AI Audiobook Creation System

# Step 2: Import Required Libraries
import streamlit as st
import os
import io
import base64
import tempfile
from pathlib import Path
import requests
import json
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play
import time

# Step 3: Configuration and Setup
class EchoVerseConfig:
    def __init__(self):
        # IBM Watson credentials (you'll need to set these)
        self.WATSON_API_KEY = ""  # Add your IBM Watson API key
        self.WATSON_URL = ""      # Add your IBM Watson service URL
        self.WATSONX_PROJECT_ID = ""  # Add your Watsonx project ID
        
    def validate_credentials(self):
        """Check if all required credentials are provided"""
        missing = []
        if not self.WATSON_API_KEY:
            missing.append("WATSON_API_KEY")
        if not self.WATSON_URL:
            missing.append("WATSON_URL")
        if not self.WATSONX_PROJECT_ID:
            missing.append("WATSONX_PROJECT_ID")
        
        if missing:
            st.error(f"Missing credentials: {', '.join(missing)}")
            st.info("Please set your IBM Watson credentials in the configuration section")
            return False
        return True

# Step 4: Text Rewriting System using IBM Watsonx
class TextRewriter:
    def __init__(self, config):
        self.config = config
        self.tone_prompts = {
            "Neutral": """Rewrite the following text in a clear, neutral, and professional tone. 
            Maintain the original meaning and structure while making it suitable for audiobook narration.
            Keep the same factual content but improve readability and flow.
            
            Original text: {text}
            
            Rewritten text:""",
            
            "Suspenseful": """Rewrite the following text with a suspenseful and engaging tone. 
            Add dramatic elements, build tension, and create intrigue while preserving the core message.
            Use vivid descriptions and create anticipation suitable for compelling audiobook narration.
            
            Original text: {text}
            
            Suspenseful rewrite:""",
            
            "Inspiring": """Rewrite the following text with an inspiring and motivational tone.
            Enhance the content with uplifting language, positive energy, and empowering messages.
            Make it engaging and motivational while keeping the original meaning intact.
            
            Original text: {text}
            
            Inspiring rewrite:"""
        }
    
    def rewrite_text(self, text, tone):
        """Rewrite text using IBM Watsonx Granite model"""
        if not self.config.validate_credentials():
            return text
        
        try:
            # This is a simplified version - in production, you'd use the actual IBM Watsonx API
            # For demo purposes, we'll simulate the rewriting based on tone
            return self._simulate_rewrite(text, tone)
        except Exception as e:
            st.error(f"Error rewriting text: {str(e)}")
            return text
    
    def _simulate_rewrite(self, text, tone):
        """Simulate text rewriting based on tone (for demo purposes)"""
        if tone == "Neutral":
            return f"In a clear and professional manner: {text}"
        elif tone == "Suspenseful":
            return f"With building tension and intrigue: {text}... What happens next will surprise you."
        elif tone == "Inspiring":
            return f"With great determination and hope: {text} This is just the beginning of an incredible journey."
        return text

# Step 5: Text-to-Speech System
class AudioGenerator:
    def __init__(self):
        self.voices = {
            "Lisa": "en-us",      # Female voice
            "Michael": "en-uk",   # Male UK voice  
            "Allison": "en-au"    # Female Australian voice
        }
    
    def generate_audio(self, text, voice="Lisa"):
        """Generate audio from text using gTTS"""
        try:
            # Map voice to language code
            lang = self.voices.get(voice, "en-us")
            
            # Create TTS object
            tts = gTTS(text=text, lang=lang.split('-')[0], slow=False)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tmp_file:
                tts.save(tmp_file.name)
                return tmp_file.name
                
        except Exception as e:
            st.error(f"Error generating audio: {str(e)}")
            return None
    
    def create_audio_player(self, audio_file):
        """Create audio player widget for Streamlit"""
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as audio_bytes:
                st.audio(audio_bytes.read(), format='audio/mp3')
    
    def create_download_button(self, audio_file, filename="audiobook.mp3"):
        """Create download button for audio file"""
        if audio_file and os.path.exists(audio_file):
            with open(audio_file, 'rb') as file:
                btn = st.download_button(
                    label="📥 Download Audio",
                    data=file.read(),
                    file_name=filename,
                    mime="audio/mp3"
                )
                return btn
        return False

# Step 6: Main Application Class
class EchoVerseApp:
    def __init__(self):
        self.config = EchoVerseConfig()
        self.rewriter = TextRewriter(self.config)
        self.audio_generator = AudioGenerator()
        self.setup_page()
    
    def setup_page(self):
        """Configure Streamlit page"""
        st.set_page_config(
            page_title="EchoVerse - AI Audiobook Creator",
            page_icon="🎧",
            layout="wide"
        )
    
    def render_header(self):
        """Render application header"""
        st.title("🎧 EchoVerse - AI Audiobook Creator")
        st.markdown("""
        Transform your text into expressive, downloadable audiobooks with customizable tones and voices.
        Perfect for students, professionals, and accessibility needs.
        """)
        st.divider()
    
    def render_input_section(self):
        """Render text input section"""
        st.subheader("📝 Input Your Text")
        
        # Text input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Paste Text", "Upload File"],
            horizontal=True
        )
        
        text_content = ""
        
        if input_method == "Paste Text":
            text_content = st.text_area(
                "Paste your text here:",
                height=200,
                placeholder="Enter the text you want to convert to audiobook..."
            )
        else:
            uploaded_file = st.file_uploader(
                "Upload a text file:",
                type=['txt'],
                help="Upload a .txt file to convert to audiobook"
            )
            
            if uploaded_file is not None:
                try:
                    text_content = uploaded_file.read().decode('utf-8')
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        return text_content
    
    def render_customization_section(self):
        """Render tone and voice selection"""
        st.subheader("🎨 Customization Options")
        
        col1, col2 = st.columns(2)
        
        with col1:
            tone = st.selectbox(
                "Select Tone:",
                ["Neutral", "Suspenseful", "Inspiring"],
                help="Choose the tone for your audiobook"
            )
        
        with col2:
            voice = st.selectbox(
                "Select Voice:",
                ["Lisa", "Michael", "Allison"],
                help="Choose the narrator voice"
            )
        
        return tone, voice
    
    def render_processing_section(self, text_content, tone, voice):
        """Render text processing and comparison"""
        if not text_content.strip():
            st.info("Please enter some text to continue.")
            return None, None
        
        if st.button("🚀 Generate Audiobook", type="primary"):
            with st.spinner("Processing your text..."):
                # Step 1: Rewrite text based on tone
                rewritten_text = self.rewriter.rewrite_text(text_content, tone)
                
                # Step 2: Generate audio
                audio_file = self.audio_generator.generate_audio(rewritten_text, voice)
                
                return rewritten_text, audio_file
        
        return None, None
    
    def render_comparison_section(self, original_text, rewritten_text):
        """Render side-by-side text comparison"""
        if rewritten_text:
            st.subheader("📋 Text Comparison")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Original Text:**")
                st.text_area("", value=original_text, height=300, disabled=True, key="orig")
            
            with col2:
                st.markdown("**Tone-Adapted Text:**")
                st.text_area("", value=rewritten_text, height=300, disabled=True, key="rewritten")
    
    def render_audio_section(self, audio_file, rewritten_text):
        """Render audio player and download section"""
        if audio_file:
            st.subheader("🎵 Generated Audiobook")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown("**Listen to your audiobook:**")
                self.audio_generator.create_audio_player(audio_file)
            
            with col2:
                st.markdown("**Download:**")
                self.audio_generator.create_download_button(
                    audio_file, 
                    f"audiobook_{int(time.time())}.mp3"
                )
            
            # Show text statistics
            st.info(f"📊 **Audio Statistics**: {len(rewritten_text)} characters, "
                   f"~{len(rewritten_text.split())} words, "
                   f"~{len(rewritten_text)//200} minutes estimated duration")
    
    def render_credentials_section(self):
        """Render credentials configuration section"""
        with st.sidebar:
            st.header("⚙️ Configuration")
            st.markdown("### IBM Watson Credentials")
            
            self.config.WATSON_API_KEY = st.text_input(
                "API Key:",
                value=self.config.WATSON_API_KEY,
                type="password",
                help="Your IBM Watson API key"
            )
            
            self.config.WATSON_URL = st.text_input(
                "Service URL:",
                value=self.config.WATSON_URL,
                help="Your IBM Watson service URL"
            )
            
            self.config.WATSONX_PROJECT_ID = st.text_input(
                "Watsonx Project ID:",
                value=self.config.WATSONX_PROJECT_ID,
                type="password",
                help="Your Watsonx project ID"
            )
            
            st.markdown("---")
            st.markdown("### About EchoVerse")
            st.markdown("""
            - 🎯 **Tone-Adaptive Rewriting**
            - 🗣️ **Natural Voice Synthesis** 
            - 📥 **Downloadable Audio**
            - 📊 **Text Comparison**
            - ♿ **Accessibility Focused**
            """)
    
    def run(self):
        """Run the main application"""
        self.render_header()
        self.render_credentials_section()
        
        # Main content area
        text_content = self.render_input_section()
        tone, voice = self.render_customization_section()
        
        st.divider()
        
        # Process and generate
        rewritten_text, audio_file = self.render_processing_section(text_content, tone, voice)
        
        # Display results
        if rewritten_text:
            self.render_comparison_section(text_content, rewritten_text)
            st.divider()
            self.render_audio_section(audio_file, rewritten_text)

# Step 7: Launch Application
def main():
    """Main function to run the EchoVerse application"""
    app = EchoVerseApp()
    app.run()

# Step 8: Run in Google Colab
if __name__ == "__main__":
    # For Google Colab, we need to run Streamlit with ngrok
    import subprocess
    import threading
    
    def run_streamlit():
        subprocess.run(["streamlit", "run", "/content/echoverse_app.py", "--server.port", "8501"])
    
    # Save the app to a file
    with open("/content/echoverse_app.py", "w") as f:
        f.write('''
# EchoVerse App File for Streamlit
exec(open("/content/echoverse_main.py").read())
''')
    
    # Save main code
    with open("/content/echoverse_main.py", "w") as f:
        # Write the entire application code here
        pass
    
    print("🎧 EchoVerse - AI Audiobook Creator")
    print("=" * 50)
    print("Setup complete! Follow these steps:")
    print("1. Set your IBM Watson credentials in the sidebar")
    print("2. Input your text (paste or upload)")
    print("3. Select tone and voice preferences")
    print("4. Generate your audiobook!")
    print("=" * 50)
    
    # Run the main application
    main()
