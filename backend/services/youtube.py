import re
from youtube_transcript_api import YouTubeTranscriptApi

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    try:
        # 1. Fetch all available transcripts for the video
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.list(video_id)

        
        try:
            # 2. Try to get the manual English one first
            transcript = transcript_list.find_transcript(['en', 'en-US'])
        except:
            # 3. If that fails, grab the auto-generated English one!
            generated_transcripts = [t for t in transcript_list if t.is_generated]
            if not generated_transcripts:
                return "Error: No English or auto-generated transcripts found."
            transcript = generated_transcripts[0] # Grab the first available auto-caption
            
        # 4. Fetch the text and combine it
        transcript_data = transcript.fetch()
        return " ".join([item.text for item in transcript_data])
        
    except Exception as e:
        # THIS is how we debug! We print the exact error to your terminal.
        print(f"\n--- DEBUG LOG ---")
        print(f"Video ID: {video_id}")
        print(f"Error Details: {str(e)}")
        print(f"call list models: {ytt_api.list(video_id)}")
        print(f"-----------------\n")
        return f"Error: {str(e)}"