import re
import requests

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    try:
        # 1. Ask the open-source Piped API (which naturally bypasses YouTube's bot protection) for the video data.
        # We try two different public instances just in case one is busy.
        api_url = f"https://pipedapi.kavin.rocks/streams/{video_id}"
        response = requests.get(api_url)
        
        if response.status_code != 200:
            api_url = f"https://pipedapi.lunar.icu/streams/{video_id}"
            response = requests.get(api_url)
            
        if response.status_code != 200:
            return "Error: Could not fetch video data from proxy."
            
        data = response.json()
        subtitles = data.get("subtitles", [])
        
        if not subtitles:
            return "Error: The creator disabled subtitles for this video, or it has no captions."
            
        # 2. Grab the English subtitles (or fallback to the first available language)
        target_sub = next((sub for sub in subtitles if 'English' in sub.get('name', '')), subtitles[0])
            
        # 3. Download the actual subtitle file (.vtt format)
        vtt_response = requests.get(target_sub['url'])
        if vtt_response.status_code != 200:
            return "Error: Could not download the subtitle file."
            
        # 4. Clean up the VTT file into plain text for Gemini
        lines = vtt_response.text.split('\n')
        text_pieces = []
        
        for line in lines:
            line = line.strip()
            # Skip VTT metadata, timestamps, and empty lines
            if not line or "-->" in line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                continue
            
            # Remove formatting tags like <c.color>, <i>, <b>
            clean_line = re.sub(r'<[^>]+>', '', line).strip()
            
            # Prevent duplicate lines (VTT files often repeat lines for overlapping captions)
            if clean_line and (not text_pieces or text_pieces[-1] != clean_line):
                text_pieces.append(clean_line)
                
        return " ".join(text_pieces)

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"