import re
import requests
import yt_dlp

def get_video_id(url: str):
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11}).*", url)
    return match.group(1) if match else None

def get_transcript(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"

    # We use yt-dlp's advanced client spoofing to completely bypass the bots.
    ydl_opts = {
        'quiet': True,
        'skip_download': True,           # We don't want the video, just the text
        'writesubtitles': True,
        'writeautomaticsub': True,
        'subtitleslangs': ['en'],
        # The ultimate bypass: impersonate a real mobile device
        'extractor_args': {'youtube': {'player_client': ['web', 'android']}}
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Securely extract the video data without downloading it
            info = ydl.extract_info(url, download=False)

            subs = info.get('requested_subtitles')
            if not subs or 'en' not in subs:
                return "Error: No English subtitles found for this video."

            # yt-dlp gives us the raw, authenticated URL to the subtitle file
            sub_url = subs['en']['url']

            # Download the text file directly
            resp = requests.get(sub_url)
            if resp.status_code != 200:
                return "Error: Could not download the subtitle file."

            # Clean the VTT data into plain text for Gemini
            lines = resp.text.split('\n')
            text_pieces = []
            for line in lines:
                line = line.strip()
                # Skip VTT metadata and timestamps
                if not line or "-->" in line or line.startswith("WEBVTT") or line.startswith("Kind:") or line.startswith("Language:"):
                    continue
                
                # Remove formatting tags (like <b> or <i>)
                clean_line = re.sub(r'<[^>]+>', '', line).strip()
                
                # Prevent duplicate lines
                if clean_line and (not text_pieces or text_pieces[-1] != clean_line):
                    text_pieces.append(clean_line)

            return " ".join(text_pieces)

    except Exception as e:
        error_msg = str(e).lower()
        if "private" in error_msg:
            return "Error: This video is private or unavailable."
        return f"Error: Video processing failed ({str(e)})"