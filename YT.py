import streamlit as st
from dotenv import load_dotenv

load_dotenv() ##load all the nevironment variables
import os
import google.generativeai as genai

from youtube_transcript_api import YouTubeTranscriptApi

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

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


## getting the transcript data from yt videos
def extract_transcript_details(youtube_video_url):
    try:
        video_id=youtube_video_url.split("=")[1]
        if len(video_id)>11:
            return video_id[:11]
        transcript_text=YouTubeTranscriptApi.get_transcript(video_id)

        transcript = ""
        for i in transcript_text:
            transcript += " " + i["text"]

        return transcript

    except Exception as e:
        raise e
    
## getting the summary based on Prompt from Google Gemini Pro
def generate_gemini_content(transcript_text,prompt):

    model=genai.GenerativeModel("gemini-pro")
    response=model.generate_content(prompt+transcript_text)
    return response.text

st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    print(video_id)
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text=extract_transcript_details(youtube_link)

    if transcript_text:
        summary=generate_gemini_content(transcript_text,prompt)
        st.markdown("## Detailed Notes:")
        st.write(summary)




