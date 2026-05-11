import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, cookies="backend/cookies.txt")
        try:
            # getting one manually in english if available 
            transcript = transcript_list.find_transcript(['en', 'en-US'])
        except:
            # if fails, use the auto-generated one often in videos 
            generated_transcripts = [t for t in transcript_list if t.is_generated]
            if not generated_transcripts:
                return "Error: No English or auto-generated transcripts found."
            transcript = generated_transcripts[0] # grab the first available caption 
            
        # fetch and combine 
        transcript_data = transcript.fetch()
        return " ".join([item.text for item in transcript_data])
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # edge case handling:

        # if the video is private
        if "video is unavailable" in error_msg or "private" in error_msg:
            return "Error: This video is private or unavailable. Please use a public video."
            
        # if the video is a live stream
        if "is a live stream" in error_msg or "livestream" in error_msg:
            return "Error: Cannot analyze active livestreams. Please use a completed, uploaded video."
            
        # if subtitles are disabled
        if "subtitles are disabled" in error_msg or "no transcript" in error_msg:
            return "Error: The creator disabled subtitles for this video, so the agents cannot read it."
            
        # any other error
        return f"Error: Could not extract transcript, ({str(e)})"