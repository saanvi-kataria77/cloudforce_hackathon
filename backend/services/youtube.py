import re
import requests

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    # The failover list: 5 different public API instances.
    instances = [
        "https://pipedapi.kavin.rocks",
        "https://pipedapi.tokhmi.xyz",
        "https://pipedapi.smnz.de",
        "https://pi.ggtyler.dev/api",
        "https://piped-api.lunar.icu"
    ]
    
    for instance in instances:
        try:
            # We set a 5-second timeout so it doesn't hang if a server is slow
            response = requests.get(f"{instance}/streams/{video_id}", timeout=5)
            
            if response.status_code == 200:
                try:
                    # THIS is where it crashed before. If it fails now, it jumps to the 'except ValueError'
                    data = response.json() 
                    subtitles = data.get("subtitles", [])
                    
                    if not subtitles:
                        continue # If this server found no subtitles, try the next server
                        
                    # Find English, or fallback to whatever the first language is
                    target_sub = next((sub for sub in subtitles if 'English' in sub.get('name', '')), subtitles[0])
                    vtt_response = requests.get(target_sub['url'], timeout=5)
                    
                    if vtt_response.status_code == 200:
                        lines = vtt_response.text.split('\n')
                        text_pieces = []
                        for line in lines:
                            line = line.strip()
                            if not line or "-->" in line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                                continue
                            clean_line = re.sub(r'<[^>]+>', '', line).strip()
                            if clean_line and (not text_pieces or text_pieces[-1] != clean_line):
                                text_pieces.append(clean_line)
                        
                        # If we successfully got the text, RETURN it and stop checking servers!
                        return " ".join(text_pieces)
                        
                except ValueError:
                    # THE FIX: If the server returns a blank page (char 0), just skip it!
                    continue 
                    
        except Exception as e:
            # If the server is completely offline and times out, skip it!
            continue

    # If it loops through ALL 5 servers and they all fail, return a graceful error to the UI
    return "Error: All proxy servers are currently busy or the video has no subtitles. Please try a different video."