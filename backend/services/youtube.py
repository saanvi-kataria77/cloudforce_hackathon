import re
import requests

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    api_url = "https://transcriptapi.com/api/v2/youtube/transcript"
    
    headers = {
        "Authorization": "Bearer sk_ON14Bl_iPjnJQpTjT8ACA_70MDRmpbHLfxK8PZc86TU"
    }
    
    params = {
        "video_url": video_id, 
        "format": "json"
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=30)
        
        if response.status_code != 200:
            return f"Error: API returned status {response.status_code}."

        data = response.json()
        
        # --- THE FINAL FIX ---
        # Look for the 'transcript' key, and verify it's a LIST
        if "transcript" in data and isinstance(data["transcript"], list):
            # Loop through every sentence dictionary, grab the 'text', and glue them together with a space!
            clean_text = " ".join([item.get("text", "") for item in data["transcript"]])
            return clean_text
            
        return "Error: Unrecognized data format."

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"