import streamlit as st
from dotenv import load_dotenv
import google.generativeai as genai
import os
from youtube_transcript_api import YouTubeTranscriptApi
from googletrans import Translator

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
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]
        return transcript
    except Exception as e:
        raise e

# Function to generate summary using Google Gemini
def generate_gemini_content(transcript_text, prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt + transcript_text)
    return response.text

# Function to translate summary to the desired language
def translate_summary(summary, language):
    translated = translator.translate(summary, dest=language)
    return translated.text

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
    ["English", "Spanish", "French", "German", "Italian", "Portuguese", "Russian", "Japanese", "Chinese", "Hindi", "Telugu", "Kannada", "Tamil"]
)

# Button to generate detailed notes
if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)

        # Translate the summary to the chosen language
        translated_summary = translate_summary(summary, language_choice)
        st.markdown("## Detailed Notes:")

        st.write(translated_summary)
