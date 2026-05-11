import re
import requests
import xml.etree.ElementTree as ET
import html

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    try:
        # 1. The Silver Bullet: Use an unblocked public transcript proxy
        response = requests.get(f"https://youtubetranscript.com/?server_vid2={video_id}")
        
        if response.status_code != 200:
            return f"Error: Could not fetch transcript (Proxy API returned {response.status_code})"
            
        # 2. Parse the XML returned by the API
        root = ET.fromstring(response.content)
        
        # 3. If the video is private or actually has no subtitles, it returns an <error> tag
        if root.tag == 'error':
            return "Error: The creator disabled subtitles for this video, or it is private/unavailable."
            
        # 4. Extract the text from all the XML <text> nodes
        transcript_pieces = [child.text for child in root if child.text]
        
        if not transcript_pieces:
            return "Error: No transcripts found."
            
        # 5. Combine into one large string and clean up HTML characters (like &amp;)
        full_transcript = " ".join(transcript_pieces)
        full_transcript = html.unescape(full_transcript)
        
        return full_transcript

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"