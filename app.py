import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi, _errors
from googletrans import Translator
import re

load_dotenv()  # Load all environment variables

# Set up Google Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Translator setup
translator = Translator()

# Define the prompt for summarization
prompt = """You are a YouTube video summarizer. You will be taking the transcript text and summarizing the entire video, providing the important points within 250 words. The transcript text will be appended here: """

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        # Extract video ID using regular expression to handle multiple URL formats
        video_id_match = re.search(r"(?<=v=)[a-zA-Z0-9_-]{11}", youtube_video_url)
        if not video_id_match:
            raise ValueError("Invalid YouTube URL")
        video_id = video_id_match.group(0)
        
        # Get transcript for the video
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for entry in transcript_text:
            transcript += " " + entry["text"]
        return transcript
    except _errors.TranscriptsDisabled:
        st.error("Transcripts are disabled for this video.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
    return None

# Function to generate summary using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Function to translate summary to the desired language
def translate_summary(summary, language):
    try:
        translated = translator.translate(summary, dest=language)
        return translated.text
    except Exception as e:
        st.error(f"Error translating summary: {e}")
        return summary

# Streamlit App Interface
st.markdown("<h1 style='color:red;'>YouTube Transcript to Detailed Notes Converter</h1>", unsafe_allow_html=True)
youtube_link = st.text_input("Enter YouTube Video Link:")

# Display thumbnail image for YouTube video
if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_container_width=True)

# Dropdown to select language for translation
language_choice = st.selectbox(
    "Choose Language for Summary:",
    ["en", "es", "fr", "de", "it", "pt", "ru", "ja", "zh", "hi", "te", "kn", "ta"]
)

# Button to generate detailed notes
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)

        if summary:
            # Translate the summary to the chosen language
            translated_summary = translate_summary(summary, language_choice)
            st.markdown("## Detailed Notes:")
            st.write(translated_summary)
