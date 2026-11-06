#!/usr/bin/env python3
"""
Direct Local Instagram Reel Publisher (No Facebook Account Required)
Uses local session caching so login credentials are only entered once.

Usage:
    # 1. First-time login test (saves session locally):
    python3 scripts/insta_local_post.py --login-only

    # 2. Upload a Reel directly:
    python3 scripts/insta_local_post.py projects/nuke-mall-part3/output/film.mp4 --caption "SURVIVAL GUIDE PART 3 🚨 #whatif #survival"
"""

import sys
import os
import getpass
import argparse
from pathlib import Path
from instagrapi import Client
from instagrapi.exceptions import (
    BadCredentials,
    TwoFactorRequired,
    ChallengeRequired,
    LoginRequired,
    ClientError
)

SESSION_DIR = Path.home() / ".config" / "stickman_video_director"
DEFAULT_SESSION_FILE = SESSION_DIR / "insta_session.json"

def get_client(session_file=DEFAULT_SESSION_FILE, username=None, password=None):
    """
    Initializes and authenticates the Instagram client using saved session or user credentials.
    """
    SESSION_DIR.mkdir(parents=True, exist_ok=True)
    cl = Client()
    # Emulate modern mobile device settings
    cl.delay_range = [1, 3]

    session_loaded = False
    if session_file.exists():
        print(f"🔑 Found saved session at: {session_file}")
        try:
            cl.load_settings(session_file)
            cl.get_timeline_feed()  # test if session cookie is still valid
            print("✅ Successfully authenticated using saved session!")
            session_loaded = True
            return cl
        except Exception as e:
            print(f"⚠️ Saved session is expired or invalid ({e}). Re-authenticating...")

    # If session not loaded, authenticate with credentials
    uname = username or os.environ.get("INSTA_USERNAME")
    pword = password or os.environ.get("INSTA_PASSWORD")

    if not session_loaded and not (uname and pword):
        if not sys.stdin.isatty():
            raise RuntimeError(
                "❌ Instagram session is invalid or missing, and no credentials were provided in CI.\n"
                "👉 Please ensure your INSTA_SESSION_JSON secret is correctly configured in your GitHub repository secrets:\n"
                "   Repo Settings -> Secrets and variables -> Actions -> INSTA_SESSION_JSON"
            )
        if not uname:
            uname = input("Instagram Username: ").strip()
        if not pword:
            pword = getpass.getpass("Instagram Password (hidden): ")

    print(f"🔄 Logging in as @{uname}...")
    try:
        cl.login(uname, pword)
    except TwoFactorRequired:
        print("🔐 Two-Factor Authentication (2FA) is enabled on this account.")
        code = input("Enter 2FA Code (from Authenticator App or SMS): ").strip()
        cl.login(uname, pword, verification_code=code)
    except ChallengeRequired:
        print("⚠️ Instagram requested a security challenge.")
        code = input("Enter the security code sent to your Email/SMS: ").strip()
        cl.login(uname, pword, verification_code=code)

    # Save session for hands-free future runs
    cl.dump_settings(session_file)
    os.chmod(session_file, 0o600)
    print(f"💾 Session successfully saved to {session_file}!")
    print("✨ Future daily uploads will use this session automatically without asking for your password.")
    return cl

def upload_reel(cl, video_path, caption="", thumbnail_path=None):
    """
    Uploads video as an Instagram Reel and prints the live post link.
    """
    video_p = Path(video_path).resolve()
    if not video_p.exists():
        raise FileNotFoundError(f"Video file does not exist: {video_p}")

    thumb_p = Path(thumbnail_path).resolve() if thumbnail_path else None
    if thumb_p and not thumb_p.exists():
        thumb_p = None

    if not caption.strip():
        caption = (
            "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\n"
            "Would you survive this scenario? Drop your answer in the comments below! 👇\n\n"
            "#whatif #survival #animation #scifi #viralreels #cartoon #reels"
        )

    print(f"\n🚀 Uploading Reel: {video_p.name} ({video_p.stat().st_size / (1024*1024):.2f} MB)...")
    print("⏳ Processing and optimizing on Instagram servers (this takes 15-40 seconds)...")

    media = cl.clip_upload(
        path=video_p,
        caption=caption,
        thumbnail=thumb_p
    )

    reel_url = f"https://www.instagram.com/reel/{media.code}/"
    print("\n" + "="*50)
    print("🎉 REEL PUBLISHED SUCCESSFULLY!")
    print(f"🔗 Live Instagram Reel URL: {reel_url}")
    print(f"🆔 Media ID: {media.pk}")
    print("="*50 + "\n")
    return media

def main():
    parser = argparse.ArgumentParser(description="Direct Local Instagram Reel Publisher (No Facebook Required)")
    parser.add_argument("video", nargs="?", help="Path to the MP4 video to upload")
    parser.add_argument("--caption", "-c", default="", help="Caption with hashtags")
    parser.add_argument("--thumbnail", "-t", default=None, help="Path to custom cover image")
    parser.add_argument("--session", default=str(DEFAULT_SESSION_FILE), help="Path to session JSON")
    parser.add_argument("--login-only", action="store_true", help="Only perform login and save session")
    parser.add_argument("--username", "-u", default=None, help="Instagram username")
    parser.add_argument("--password", "-p", default=None, help="Instagram password")

    args = parser.parse_args()

    session_path = Path(args.session)
    cl = get_client(session_file=session_path, username=args.username, password=args.password)

    if args.login_only:
        user_info = cl.account_info()
        print(f"✅ Verified Account: @{user_info.username} (ID: {user_info.pk})")
        print("Ready for automated daily posting!")
        return

    if not args.video:
        print("❌ Please specify a video file to upload, or use --login-only.")
        sys.exit(1)

    upload_reel(cl, args.video, caption=args.caption, thumbnail_path=args.thumbnail)

if __name__ == "__main__":
    main()
