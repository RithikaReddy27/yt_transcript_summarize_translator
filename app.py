import yt_dlp
import streamlit as st
from googletrans import Translator
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
translator = Translator()

# Extract video ID from YouTube URL
def extract_video_id(youtube_url):
    if "youtu.be" in youtube_url:
        return youtube_url.split("/")[-1]
    if "youtube.com/watch?v=" in youtube_url:
        return youtube_url.split("v=")[-1].split("&")[0]
    return None

# Fetch subtitles using yt-dlp
def get_subtitles(video_url, lang="en"):
    video_id = extract_video_id(video_url)
    if not video_id:
        st.error("Invalid YouTube URL")
        return None

    ydl_opts = {
        'writesubtitles': True,
        'subtitleslangs': [lang],
        'skip_download': True,
        'quiet': True,
        'force_generic_extractor': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
            subtitles = info.get("subtitles", {})
            if lang in subtitles:
                subtitle_url = subtitles[lang][-1]["url"]
                return subtitle_url  # Returns the direct subtitle URL
            else:
                st.error(f"No subtitles found in {lang}")
                return None
    except Exception as e:
        st.error(f"Error fetching subtitles: {e}")
        return None

# Generate summary using Gemini AI
def generate_gemini_summary(transcript_text):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(f"Summarize this YouTube transcript:\n\n{transcript_text}")
        return response.text
    except Exception as e:
        st.error(f"Error generating summary: {e}")
        return None

# Translate summary
def translate_summary(summary, target_lang):
    try:
        translated = translator.translate(summary, dest=target_lang)
        return translated.text
    except Exception as e:
        st.error(f"Translation error: {e}")
        return summary

# Streamlit UI
st.title("YouTube Subtitle Summarizer & Translator")
youtube_url = st.text_input("Enter YouTube Video URL:")
language = st.selectbox("Select Language:", ["English", "Spanish", "French", "Hindi", "Telugu", "Kannada", "Tamil"])

if st.button("Get Summary"):
    subtitles_url = get_subtitles(youtube_url, lang="en")
    if subtitles_url:
        transcript_text = yt_dlp.utils.download_webpage(subtitles_url)
        if transcript_text:
            summary = generate_gemini_summary(transcript_text)
            translated_summary = translate_summary(summary, language)
            st.write("### Detailed Notes:")
            st.write(translated_summary)

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
