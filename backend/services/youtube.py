import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.proxies import GenericProxyConfig

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    # 1. Paste your ScraperAPI key here
    SCRAPER_API_KEY = "6275ea5d7af5c4560531e465fdf485d2"
    
    # 2. Format the proxy URL
    proxy_url = f"http://scraperapi:{SCRAPER_API_KEY}@proxy-server.scraperapi.com:8001"
    
    # 3. Use the library's built-in proxy configuration
    proxy_config = GenericProxyConfig(
        http_url=proxy_url,
        https_url=proxy_url
    )

    try:
        # 4. Initialize the API with your VIP proxy pass
        ytt_api = YouTubeTranscriptApi(proxy_config=proxy_config)
        
        # 5. The exact command for the new library version!
        transcript_list = ytt_api.fetch(video_id)
        
        # Combine the text
        return " ".join([item['text'] for item in transcript_list])
        
    except Exception as e:
        error_msg = str(e).lower()
        if "video is unavailable" in error_msg or "private" in error_msg:
            return "Error: This video is private or unavailable."
        if "is a live stream" in error_msg or "livestream" in error_msg:
            return "Error: Cannot analyze active livestreams."
        if "disabled" in error_msg or "no transcript" in error_msg:
            return "Error: The creator disabled subtitles for this video."
            
        return f"Error: Could not extract transcript, ({str(e)})"