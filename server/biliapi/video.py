import requests
import json

def get_video_info(video_id):
    """Fetch video information from the Bilibili API."""
    url = f"https://api.bilibili.com/x/web-interface/wbi/view?bvid={video_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36 Edg/140.0.0.0"
    }
    response = requests.get(url, headers=headers)
    return response.json()
