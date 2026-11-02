#!/usr/bin/env python3
"""
Automated Instagram Reel Publisher via Make.com Webhook
Usage:
    python3 scripts/autopost_make.py <path_to_video.mp4> --caption "Your caption" --webhook "YOUR_MAKE_WEBHOOK_URL"
"""

import sys
import os
import argparse
import urllib.request
import urllib.parse
import json

def upload_video_to_cdn(video_path):
    """
    Uploads the local MP4 video to a fast, direct public file host
    so Meta's Instagram server can fetch and process the Reel.
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Video file not found: {video_path}")
    
    print(f"📦 Uploading {os.path.basename(video_path)} to fast public CDN...")
    
    boundary = "----WebKitFormBoundary7MA4YWxkTrZu0gW"
    data = []
    
    data.append(f"--{boundary}".encode())
    data.append(b'Content-Disposition: form-data; name="reqtype"')
    data.append(b'')
    data.append(b'fileupload')
    
    data.append(f"--{boundary}".encode())
    data.append(f'Content-Disposition: form-data; name="fileToUpload"; filename="{os.path.basename(video_path)}"'.encode())
    data.append(b'Content-Type: video/mp4')
    data.append(b'')
    with open(video_path, 'rb') as f:
        data.append(f.read())
        
    data.append(f"--{boundary}--".encode())
    data.append(b'')
    
    body = b'\r\n'.join(data)
    req = urllib.request.Request(
        'https://catbox.moe/user/api.php',
        data=body,
        headers={
            'Content-Type': f'multipart/form-data; boundary={boundary}',
            'User-Agent': 'Mozilla/5.0'
        }
    )
    
    with urllib.request.urlopen(req, timeout=120) as resp:
        url = resp.read().decode('utf-8').strip()
        if not url.startswith('http'):
            raise RuntimeError(f"Upload failed: {url}")
        print(f"✅ Video CDN Link: {url}")
        return url

def trigger_make_webhook(webhook_url, video_url, caption):
    """
    Sends the payload to Make.com to trigger Instagram Reel publishing.
    """
    print(f"🚀 Sending payload to Make.com webhook...")
    payload = json.dumps({
        "video_url": video_url,
        "caption": caption
    }).encode('utf-8')
    
    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={'Content-Type': 'application/json', 'User-Agent': 'Autopilot-Poster/1.0'}
    )
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        status = resp.status
        body = resp.read().decode('utf-8')
        print(f"🎉 Make.com Response [{status}]: {body}")
        print("✅ Reel has been handed off to Instagram for publishing!")

def main():
    parser = argparse.ArgumentParser(description="Post Reel to Instagram via Make.com Webhook")
    parser.add_argument("video", help="Path to the MP4 file")
    parser.add_argument("--webhook", default=os.environ.get("MAKE_WEBHOOK_URL"), help="Your Make.com Webhook URL")
    parser.add_argument("--caption", default="", help="Instagram caption")
    args = parser.parse_args()

    if not args.webhook:
        print("❌ Error: Missing Make.com Webhook URL.")
        print("Provide it via --webhook <url> or set MAKE_WEBHOOK_URL in environment.")
        sys.exit(1)

    caption = args.caption
    if not caption:
        caption = (
            "Part 3 Finale: Timeline Secured! ⏳🚨\n\n"
            "Would you close the loop or step into the unknown?\n\n"
            "#mystery #whatif #animation #timetravel #scifi #shortfilm #viral #cartoon"
        )

    cdn_url = upload_video_to_cdn(args.video)
    trigger_make_webhook(args.webhook, cdn_url, caption)

if __name__ == '__main__':
    main()
