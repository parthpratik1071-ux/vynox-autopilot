#!/usr/bin/env python3
"""
Official YouTube Shorts Uploader & AI-Content Compliance Engine for Vynox Autopilot.
Uploads 9:16 vertical videos to YouTube Shorts with official YouTube Data API v3,
automatic OAuth2 token refresh, and full compliance with YouTube's Altered & Synthetic Content disclosure.
"""

import argparse
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.readonly"]
CREDENTIALS_DIR = Path.home() / ".config" / "stickman_video_director"
LOCAL_TOKEN_FILE = CREDENTIALS_DIR / "youtube_token.json"
CLIENT_SECRET_FILE = CREDENTIALS_DIR / "youtube_client_secret.json"


def get_credentials(interactive: bool = False) -> Credentials | None:
    """
    Resolves credentials from GitHub Actions secrets / environment variables first,
    then falls back to local token JSON file.
    """
    client_id = os.environ.get("YOUTUBE_CLIENT_ID", "").strip()
    client_secret = os.environ.get("YOUTUBE_CLIENT_SECRET", "").strip()
    refresh_token = os.environ.get("YOUTUBE_REFRESH_TOKEN", "").strip()

    if client_id and client_secret and refresh_token:
        creds = Credentials(
            None,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=SCOPES,
        )
        try:
            creds.refresh(Request())
            return creds
        except Exception as e:
            print(f"⚠️ Failed to refresh YouTube credentials from environment: {e}")

    # Fallback to local token file
    if LOCAL_TOKEN_FILE.exists():
        try:
            with open(LOCAL_TOKEN_FILE, "r") as f:
                data = json.load(f)
            creds = Credentials.from_authorized_user_info(data, SCOPES)
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
                with open(LOCAL_TOKEN_FILE, "w") as f:
                    f.write(creds.to_json())
            return creds
        except Exception as e:
            print(f"⚠️ Failed to load local YouTube token: {e}")

    if interactive and CLIENT_SECRET_FILE.exists():
        print(f"🔑 Initiating OAuth flow with {CLIENT_SECRET_FILE}...")
        flow = InstalledAppFlow.from_client_secrets_file(str(CLIENT_SECRET_FILE), SCOPES)
        creds = flow.run_local_server(port=8080, prompt="consent", access_type="offline")
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOCAL_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        LOCAL_TOKEN_FILE.chmod(0o600)
        print(f"💾 YouTube credentials saved to {LOCAL_TOKEN_FILE}!")
        return creds

    return None


def get_youtube_service(creds: Credentials | None = None):
    """Builds the authorized YouTube Data API service."""
    if not creds:
        creds = get_credentials(interactive=False)
    if not creds:
        raise RuntimeError(
            "❌ YouTube credentials not configured.\n"
            "👉 Set YOUTUBE_CLIENT_ID, YOUTUBE_CLIENT_SECRET, and YOUTUBE_REFRESH_TOKEN in environment,\n"
            "   or run `python3 scripts/youtube_uploader.py --auth-setup` with client_secret.json."
        )
    return build("youtube", "v3", credentials=creds)


def check_auth_health() -> tuple[bool, str, str | None]:
    """
    Non-destructive check that tests YouTube connection and returns channel title.
    Returns (is_healthy, status_code, channel_name_or_error).
    """
    try:
        service = get_youtube_service()
        response = service.channels().list(mine=True, part="snippet,statistics").execute()
        items = response.get("items", [])
        if not items:
            return False, "CHANNEL_NOT_FOUND", "No YouTube channel linked with these credentials."
        channel_title = items[0]["snippet"]["title"]
        subscribers = items[0]["statistics"].get("subscriberCount", "Hidden")
        return True, "YOUTUBE_AUTH_HEALTHY", f"{channel_title} ({subscribers} subscribers)"
    except Exception as e:
        return False, "YOUTUBE_AUTH_FAILED", str(e)


def build_ai_compliant_description(
    song_title: str,
    artist: str,
    custom_desc: str = "",
    tags: list[str] | None = None,
) -> str:
    """
    Formats description ensuring full compliance with YouTube's 
    Altered & Synthetic Content policies and maximum Shorts SEO discovery.
    """
    desc_lines = []
    if custom_desc:
        desc_lines.append(custom_desc.strip())
        desc_lines.append("")

    desc_lines.append("──────────────────────────────")
    desc_lines.append("🎨 VISUAL & PRODUCTION CREDITS:")
    desc_lines.append("• Visual Art & Animation: Vynox Autopilot Studio (@vynox_00000)")
    desc_lines.append("• Visual Medium: 2D Anime & Stylized AI Animation")
    if song_title:
        desc_lines.append(f"• Track: {song_title}")
    if artist:
        desc_lines.append(f"• Original Artist: {artist}")
    desc_lines.append("")
    desc_lines.append("✨ TRANSPARENCY NOTICE (YouTube Synthetic Content Compliance):")
    desc_lines.append("This creative video features stylized 2D anime illustrations, generative AI visual art,")
    desc_lines.append("and custom motion animation designed for an aesthetic lofi storytelling experience.")
    desc_lines.append("──────────────────────────────")
    desc_lines.append("")
    
    # Tag block
    default_tags = ["#Shorts", "#AIAnimation", "#2DAnimation", "#HindiIndie", "#AestheticArt", "#LofiAnime"]
    all_tags = list(dict.fromkeys(default_tags + (tags or [])))
    desc_lines.append(" ".join(all_tags))

    return "\n".join(desc_lines)


def upload_short(
    video_path: str | Path,
    title: str,
    song_title: str = "",
    artist: str = "",
    description: str = "",
    privacy_status: str = "public",
    dry_run: bool = False,
) -> dict:
    """
    Uploads a vertical MP4 to YouTube as a Short.
    Ensures #Shorts tag in title and description, and AI disclosure in metadata.
    """
    vid_file = Path(video_path).resolve()
    if not vid_file.exists():
        raise FileNotFoundError(f"Video file not found: {vid_file}")

    # Ensure #Shorts tag is in title for algorithmic shelf indexing
    if "#Shorts" not in title and "#shorts" not in title:
        short_title = f"{title.strip()} #Shorts"
    else:
        short_title = title.strip()

    # YouTube titles are max 100 characters
    if len(short_title) > 100:
        short_title = short_title[:92].strip() + " #Shorts"

    final_description = build_ai_compliant_description(
        song_title=song_title,
        artist=artist,
        custom_desc=description,
    )

    tags = [
        "Shorts",
        "YouTube Shorts",
        "AI Animation",
        "2D Anime",
        "Aesthetic Reels",
        "Hindi Indie",
        "Lofi Animation",
        "Vynox Studio",
    ]
    if song_title:
        tags.append(song_title)
    if artist:
        tags.append(artist)

    body = {
        "snippet": {
            "title": short_title,
            "description": final_description,
            "tags": tags,
            "categoryId": "10",  # 10 = Music, 1 = Film & Animation
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False,
            "embeddable": True,
            "license": "youtube",
        },
    }

    if dry_run:
        print("\n🧪 [DRY RUN] YouTube Shorts Metadata Prepared:")
        print(f"Title: {body['snippet']['title']}")
        print(f"Privacy: {body['status']['privacyStatus']}")
        print(f"Tags: {', '.join(body['snippet']['tags'])}")
        print(f"Video File: {vid_file} ({vid_file.stat().st_size / (1024*1024):.2f} MB)")
        print("\nDescription Preview:\n" + body["snippet"]["description"][:300] + "...\n")
        return {"id": "dry_run_id", "title": short_title, "status": "dry_run"}

    service = get_youtube_service()
    media = MediaFileUpload(
        str(vid_file),
        mimetype="video/mp4",
        chunksize=1024 * 1024 * 5,  # 5MB chunks
        resumable=True,
    )

    print(f"🚀 Uploading YouTube Short: {short_title} ({vid_file.name})...")
    request = service.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"⏳ Upload progress: {int(status.progress() * 100)}%")

    video_id = response.get("id")
    short_url = f"https://youtube.com/shorts/{video_id}"
    print(f"✅ Successfully published YouTube Short!")
    print(f"🔗 Video URL: {short_url}")
    return response


def main():
    parser = argparse.ArgumentParser(description="Official YouTube Shorts Uploader with AI Disclosure")
    parser.add_argument("video", nargs="?", help="Path to the MP4 video to upload")
    parser.add_argument("--title", "-t", default="", help="Short title (must include or will auto-append #Shorts)")
    parser.add_argument("--song", default="", help="Song name for credit and SEO")
    parser.add_argument("--artist", default="", help="Artist name for credit and SEO")
    parser.add_argument("--description", "-d", default="", help="Custom description text")
    parser.add_argument("--privacy", choices=["public", "private", "unlisted"], default="public", help="Video visibility")
    parser.add_argument("--check-auth", action="store_true", help="Test YouTube authentication and exit")
    parser.add_argument("--auth-setup", action="store_true", help="Interactive OAuth setup to generate refresh token")
    parser.add_argument("--auth-code", help="Complete OAuth flow by providing authorization code or full redirect URL")
    parser.add_argument("--dry-run", action="store_true", help="Validate metadata and video without uploading")

    args = parser.parse_args()

    if args.auth_setup:
        if CLIENT_SECRET_FILE.exists():
            print("\n" + "=" * 60)
            print("🔑 Opening browser for YouTube Channel authorization...")
            print("=" * 60)
            try:
                creds = get_credentials(interactive=True)
                if creds:
                    print("\n🎉 Authentication Successful!")
                    print("=" * 60)
                    print("Copy these values for GitHub Actions Secrets:")
                    print("=" * 60)
                    print(f"• YOUTUBE_CLIENT_ID: {creds.client_id}")
                    print(f"• YOUTUBE_CLIENT_SECRET: {creds.client_secret}")
                    print(f"• YOUTUBE_REFRESH_TOKEN: {creds.refresh_token}")
                    print("=" * 60 + "\n")
                    return
            except Exception as e:
                print(f"⚠️ Automatic local server flow failed ({e}).")
        else:
            print(f"❌ Missing client secret file: {CLIENT_SECRET_FILE}")
        return

    if args.auth_code:
        import urllib.parse
        code = args.auth_code.strip()
        if "code=" in code:
            parsed = urllib.parse.urlparse(code)
            params = urllib.parse.parse_qs(parsed.query or parsed.fragment)
            code = params.get("code", [code])[0]

        flow = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET_FILE),
            SCOPES,
            redirect_uri="http://localhost:8080/",
        )
        flow.fetch_token(code=code)
        creds = flow.credentials
        CREDENTIALS_DIR.mkdir(parents=True, exist_ok=True)
        with open(LOCAL_TOKEN_FILE, "w") as f:
            f.write(creds.to_json())
        LOCAL_TOKEN_FILE.chmod(0o600)
        print("\n🎉 Token Generated & Saved Successfully!")
        print(f"• YOUTUBE_CLIENT_ID: {creds.client_id}")
        print(f"• YOUTUBE_CLIENT_SECRET: {creds.client_secret}")
        print(f"• YOUTUBE_REFRESH_TOKEN: {creds.refresh_token}\n")
        return

    if args.check_auth:
        ok, code, detail = check_auth_health()
        if ok:
            print(f"✅ YouTube Authentication HEALTHY: {detail}")
            sys.exit(0)
        else:
            print(f"⚠️ YouTube Authentication REQUIRED ({code}): {detail}")
            sys.exit(2)

    if not args.video:
        parser.print_help()
        sys.exit(1)

    title = args.title or Path(args.video).stem.replace("_", " ").title()
    upload_short(
        video_path=args.video,
        title=title,
        song_title=args.song,
        artist=args.artist,
        description=args.description,
        privacy_status=args.privacy,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()

