import re
import requests

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    api_url = "https://transcriptapi.com/api/v2/youtube/transcript"
    
    # Using your active key to cross the finish line
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
            return f"Error: API returned status {response.status_code}. Raw: {response.text}"

        data = response.json()
        
        # --- THE FIX: Look for the exact key your snippet showed! ---
        if "transcript" in data and isinstance(data["transcript"], str):
            clean_text = data["transcript"].strip()
            if clean_text:
                return clean_text

        # Fallback just in case they sometimes use "text" or "segments"
        if "segments" in data and data["segments"]:
            return " ".join([seg.get("text", "") for seg in data["segments"]])
            
        if "text" in data and isinstance(data["text"], str):
            return data["text"]

        # --- THE SAFETY NET ---
        # If it STILL fails, we force Python to print exactly what the API sent us
        # so you can see it in your Render dashboard logs.
        print(f"\n--- RAW API DATA FOR {video_id} ---")
        print(data)
        print("-----------------------------------\n")
        
        return "Error: Connected successfully, but couldn't parse the text. Check Render logs!"

    except Exception as e:
        return f"Error: Could not extract transcript, ({str(e)})"