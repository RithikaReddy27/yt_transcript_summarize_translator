import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable
from googletrans import Translator
import re
import urllib.parse

load_dotenv()  # Load environment variables

# Configure Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Translator setup
translator = Translator()

# Define summarization prompt
prompt = "Summarize the given YouTube transcript into key points within 250 words: "

# Function to extract video ID from various YouTube URL formats
def extract_video_id(url):
    try:
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.netloc in ["www.youtube.com", "youtube.com"]:
            query_params = urllib.parse.parse_qs(parsed_url.query)
            return query_params.get("v", [None])[0]
        elif parsed_url.netloc == "youtu.be":
            return parsed_url.path.lstrip("/")
        elif "embed" in parsed_url.path:
            return parsed_url.path.split("/")[-1]
        return None
    except Exception:
        return None

# Function to extract transcript
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        if not video_id:
            st.error("Invalid YouTube URL format. Please check and try again.")
            return None
        
        transcript_data = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([entry["text"] for entry in transcript_data])
        return transcript

    except TranscriptsDisabled:
        st.error("❌ Transcripts are disabled for this video.")
    except NoTranscriptFound:
        st.error("❌ No transcript found for this video. Try another one.")
    except VideoUnavailable:
        st.error("❌ This video is unavailable. Please check the link.")
    except Exception as e:
        st.error(f"⚠️ An unexpected error occurred: {e}")
    return None

# Function to generate summary using Google Gemini
def generate_gemini_content(transcript_text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"⚠️ Error generating summary: {e}")
        return None

# Function to translate summary
def translate_summary(summary, language):
    try:
        translated = translator.translate(summary, dest=language)
        return translated.text
    except Exception as e:
        st.error(f"⚠️ Error translating summary: {e}")
        return summary

# Streamlit UI
st.markdown("<h1 style='color:red;'>YouTube Transcript Summarizer & Translator</h1>", unsafe_allow_html=True)

youtube_link = st.text_input("🔗 Enter YouTube Video Link:")

# Display thumbnail if URL is valid
video_id = extract_video_id(youtube_link)
if video_id:
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

# Language selection
language_choice = st.selectbox("🌍 Choose Language for Summary:", 
    ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Chinese", "Hindi", "Telugu", "Kannada", "Tamil"]
)

# Button to generate summary
if st.button("📜 Get Detailed Notes"):
    with st.spinner("⏳ Fetching transcript..."):
        transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        with st.spinner("🤖 Generating summary..."):
            summary = generate_gemini_content(transcript_text)

        if summary:
            with st.spinner("🌍 Translating summary..."):
                translated_summary = translate_summary(summary, language_choice)

            st.markdown("## 📌 Detailed Notes:")
            st.write(translated_summary)
