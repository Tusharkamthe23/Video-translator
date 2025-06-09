import streamlit as st
from youtube_transcript_api import YouTubeTranscriptApi
from deep_translator import GoogleTranslator
from gtts import gTTS
import tempfile
import os
import re
import textwrap
from youtube_transcript_api.proxies import WebshareProxyConfig

ytt_api = YouTubeTranscriptApi(
    proxy_config=WebshareProxyConfig(
        proxy_username=username,
        proxy_password=password,
    )
)

# --- Extract YouTube Video ID ---
def extract_video_id(url):
    pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    match = re.search(pattern, url)
    if not match:
        raise ValueError("Invalid YouTube URL")
    return match.group(1)

# --- Get Transcript ---
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        return " ".join([entry["text"] for entry in transcript])
    except TranscriptsDisabled:
        raise ValueError("Transcripts are disabled for this video.")
    except NoTranscriptFound:
        raise ValueError("No transcript available for this video.")
    except VideoUnavailable:
        raise ValueError("The video is unavailable.")
    except Exception as e:
        raise ValueError(f"Failed to fetch transcript: {e}")

# --- Translate Transcript in Chunks ---
def translate_text(text, target_lang='es', chunk_size=4500):
    chunks = textwrap.wrap(text, chunk_size)
    translated = [GoogleTranslator(target=target_lang).translate(chunk) for chunk in chunks]
    return " ".join(translated)

# --- Convert Text to Speech ---
def text_to_speech(text, lang='es'):
    tts = gTTS(text=text, lang=lang)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(tmp_file.name)
    return tmp_file.name

# --- Streamlit UI ---
st.set_page_config(page_title="Video Translator & Dubber", layout="centered")
st.title("🎙️ video Translator & Dubber")

youtube_url = st.text_input("Enter YouTube video URL:")
language_names = {
    "hi": "Hindi",
    "mr": "Marathi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
    "as": "Assamese",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "zh-cn": "Chinese (Simplified)",
    "ja": "Japanese",
    "ru": "Russian",
    "pt": "Portuguese",
    "en": "English"
}

# Reverse mapping to get code from name
reverse_lang_map = {v: k for k, v in language_names.items()}
selected_lang_name = st.selectbox("Select translation language:", list(language_names.values()))
language = reverse_lang_map[selected_lang_name]

if st.button("Translate and Generate Audio"):
    
    try:
        with st.spinner("Processing..."):
            video_id = extract_video_id(youtube_url)
            st.write("Extracted Video ID:", video_id)
            transcript = get_transcript(video_id)
            st.text_area("Original Transcript", transcript, height=200)

            translated_text = translate_text(transcript, target_lang=language)
            audio_file = text_to_speech(translated_text, lang=language)

        st.success("Translation and audio generation complete!")

        # Show video via embed
        st.video(f"https://www.youtube.com/embed/{video_id}")

        # Audio playback
        st.audio(audio_file)

        # Optional: Download transcript
        st.download_button("Download Translated Transcript", translated_text, file_name="translated_transcript.txt")

    except Exception as e:
        st.error(f"Error: {e}")
