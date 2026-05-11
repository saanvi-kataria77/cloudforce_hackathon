import re
import requests
import xml.etree.ElementTree as ET
import html

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    try:

        # 1. telling the proxy we are a real human using Google Chrome
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'
        }
        # 2. pass in disguise
        response = requests.get(
            f"https://youtubetranscript.com/?server_vid2={video_id}",
            headers=headers
        )
        
        if response.status_code != 200:
            return f"Error: Could not fetch transcript (Proxy API returned {response.status_code})"
            
        # 2. parse the XML returned by the API
        root = ET.fromstring(response.content)
        
        # 3. if the video is private or actually has no subtitles, it returns an <error> tag
        if root.tag == 'error':
            return "Error: The creator disabled subtitles for this video, or it is private/unavailable."
            
        # 4. extract the text from all the XML <text> nodes
        transcript_pieces = [child.text for child in root if child.text]
        
        if not transcript_pieces:
            return "Error: No transcripts found."
            
        # 5. combine into one large string and clean up HTML characters (like &amp;)
        full_transcript = " ".join(transcript_pieces)
        full_transcript = html.unescape(full_transcript)
        
        return full_transcript

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"