import re
import requests

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    # 1. The dedicated TranscriptAPI endpoint
    api_url = "https://transcriptapi.com/api/v2/youtube/transcript"
    
    # 2. Paste your free API key here
    headers = {
        "Authorization": "Bearer sk_ON14Bl_iPjnJQpTjT8ACA_70MDRmpbHLfxK8PZc86TU"
    }
    
    # 3. They just need the full video URL and the format you want
    params = {
        "video_url": f"https://www.youtube.com/watch?v={video_id}",
        "format": "json"
    }

    try:
        response = requests.get(api_url, headers=headers, params=params)
        
        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}. The video might be private."

        data = response.json()
        segments = data.get("segments", [])
        
        if not segments:
            return "Error: No transcript found or subtitles are disabled."
            
        # 4. Combine the text segments into one massive string for Gemini
        clean_text = " ".join([segment.get("text", "") for segment in segments])
        
        return clean_text

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"