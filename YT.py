import streamlit as st
from dotenv import load_dotenv
import re
#load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

# Load API key from environment variables( create '.env' file in the project directory in vs code to store your API KEY, e.g GOOGLE_API_KEY=" ")
API_KEY =st.secrets["GOOGLE_API_KEY"] # it will be 'os.getenv["GOOGLE_API_KEY"]' in Vscode
genai.configure(api_key=API_KEY)

prompt="""
Notes should have a sample format like this:
Title: Comprehensive Notes from YouTube Video Transcript

            Subject: give it a title

            Prompt:

            an expert with all knowledge, tasked  to provide comprehensive notes based on the transcript of a YouTube video  provided. Assumed the role of a student and generate detailed notes covering the key concepts discussed in the video.

            Your notes should:

            Subject:

            Explaination fundamental concepts 

            Outlining basic  concepts 

            notes aims to offer a clear understanding of both the theoretical foundations and practical applications of subject discussed in the video. Use clear explanations, examples, and visuals where necessary to enhance comprehension.

            
         """

#Below code was working for only video link copied from a computer. It was not working for video link copied from mobile device


# ## getting the transcript data from yt videos
# def extract_transcript_details(youtube_video_url):
#     try:
#         video_id=youtube_video_url.split("=")[1]
#         if len(video_id)>11:
#             return video_id[:11]
#         transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

#         transcript = ""
#         for i in transcript_text:
#             transcript += " " + i["text"]

#         return transcript

#     except Exception as e:
#         raise e
    
## getting the transcript data from yt videos to work for both mobile and computer
def extract_video_id(youtube_video_url):
    """
    Extracts the video ID from a YouTube URL.
    """
    if 'youtu.be' in youtube_video_url:
        # This is a shortened URL, the video ID follows after the last '/'
        video_id = youtube_video_url.split('/')[-1]
        # Remove any additional URL parameters if present
        video_id = video_id.split('?')[0]
        return video_id
    else:
        # This is a regular URL, we use a regex to extract the video ID
        match = re.search(r"v=([a-zA-Z0-9_-]{11})", youtube_video_url)
        return match.group(1) if match else None
# extracting trancript details from video link
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join(segment["text"] for segment in transcript_list)
        return transcript

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
## getting the summary based on Prompt from Google Gemini Pro
def extract_transcript_details(youtube_video_url):
    try:
        video_id = extract_video_id(youtube_video_url)
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id)

        transcript = " ".join(segment["text"] for segment in transcript_list)
        return transcript

    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            prompt + transcript_text,
            safety_settings=[
                {
                    "category": "HARM_CATEGORY_HARASSMENT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_HATE_SPEECH",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
                {
                    "category": "HARM_CATEGORY_DANGEROUS",
                    "threshold": "BLOCK_LOW_AND_ABOVE",
                },
            ]
        )
        
        # If the response has candidates, will return the first candidate's text
        if hasattr(response, 'candidates') and response.candidates:
            return response.candidates[0].text
        else:
            # If the content was blocked, check the prompt feedback for safety reasons
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                # Here you may need to adjust based on the actual structure of the prompt feedback
                for rating in response.prompt_feedback.safety_ratings:
                    if rating.probability == 'HIGH':
                        st.error("The video content has been flagged for containing harmful content.")
                        return None
                st.error("The content generation was blocked or failed Because video contain harmful content.")
            else:
                st.error("No candidates were returned, and no specific feedback was provided.")
            return None
    
    except Exception as e:
        st.error(f"An error occurred while generating content: {e}")
        return None

st.set_page_config(page_title="Chat with YouTube Video")
st.header("YouTube Transcript to Detailed Notes Converter")

# Input for user YouTube link
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = extract_video_id(youtube_link)
    if video_id:
        # Display the thumbnail of the video
        thumbnail_url = f"http://img.youtube.com/vi/{video_id}/0.jpg"
        st.image(thumbnail_url, caption='Video Thumbnail', use_column_width=True)
    else:
        st.error("Could not extract the video ID. Please check the YouTube link.")


if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)
        if summary:
            st.markdown("## Detailed Notes:")
            st.write(summary)
        else:
            st.error("Failed to generate detailed notes. The model response was not as expected Because Content seems harmful.")
    else:
        st.error("Could not extract the transcript. Please check the YouTube link.")




