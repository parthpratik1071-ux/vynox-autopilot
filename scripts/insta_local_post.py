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
import json
import re
import time
import getpass
import argparse
import subprocess
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from types import SimpleNamespace
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
GRAPH_API_BASE = "https://graph.facebook.com/v21.0"


def is_restriction_error(exc: Exception) -> bool:
    """Returns True when Instagram signals a login, challenge, or action/restriction block."""
    name = type(exc).__name__.lower()
    msg = str(exc).lower()
    markers = (
        "challengerequired",
        "feedbackrequired",
        "loginrequired",
        "pleasewaitfewminutes",
        "challenge_required",
        "feedback_required",
        "login_required",
        "restrict",
        "try again later",
        "spam",
        "checkpoint",
    )
    return any(m in name or m in msg for m in markers)


def _derive_public_media_url(local_path: Path) -> str | None:
    """Builds a public raw.githubusercontent.com URL for repo-tracked media files."""
    repo_root = Path(__file__).resolve().parent.parent
    try:
        rel = local_path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return None

    base = os.environ.get("PUBLIC_MEDIA_BASE_URL", "").strip().rstrip("/")
    if base:
        return f"{base}/{urllib.parse.quote(rel)}"

    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"], cwd=str(repo_root), text=True
        ).strip()
        m = re.search(r"github\.com[:/]([^/]+/[^/.]+?)(?:\.git)?$", remote)
        if m:
            return f"https://raw.githubusercontent.com/{m.group(1)}/main/{urllib.parse.quote(rel)}"
    except Exception:
        pass
    return None


class OfficialGraphClient:
    """
    Zero-ban-risk Meta Official Instagram Graph API v21.0 client.
    Mirrors the subset of `instagrapi.Client` methods used by daily_dispatcher & reels_booster.
    Requires a Professional (Creator/Business) account + INSTA_GRAPH_ACCESS_TOKEN + INSTA_IG_USER_ID.
    """

    def __init__(self, access_token: str, ig_user_id: str):
        self.access_token = access_token.strip()
        self.user_id = str(ig_user_id).strip()
        self.is_official_graph = True

    def _request(self, path: str, params: dict | None = None, method: str = "GET") -> dict:
        query = dict(params or {})
        query["access_token"] = self.access_token
        encoded = urllib.parse.urlencode(query)
        url = f"{GRAPH_API_BASE}/{path.lstrip('/')}"
        if method == "GET":
            req = urllib.request.Request(f"{url}?{encoded}", method="GET")
        else:
            req = urllib.request.Request(url, data=encoded.encode(), method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            detail = e.read().decode(errors="ignore")
            raise RuntimeError(f"Graph API {e.code}: {detail}") from e

    def account_info(self):
        info = self._request(self.user_id, {"fields": "id,username"})
        return SimpleNamespace(pk=info.get("id", self.user_id), username=info.get("username", "unknown"))

    def _fetch_reel_plays(self, media_id: str) -> int:
        """Fetches Reel play/view count via Graph API insights, falling back to 0."""
        if not media_id:
            return 0
        for metric in ("plays", "views"):
            try:
                ins = self._request(f"{media_id}/insights", {"metric": metric})
                values = (ins.get("data") or [{}])[0].get("values") or [{}]
                return int(values[0].get("value", 0) or 0)
            except Exception:
                continue
        return 0

    def user_medias(self, uid: str, amount: int = 10) -> list:
        res = self._request(
            f"{self.user_id}/media",
            {"fields": "id,caption,permalink,timestamp,like_count,comments_count,media_type", "limit": amount},
        )
        items = []
        for row in res.get("data", []):
            code_match = re.search(r"/(?:reel|p)/([^/]+)/", row.get("permalink", ""))
            taken_raw = row.get("timestamp", "")
            try:
                taken_at = datetime.fromisoformat(taken_raw.replace("Z", "+00:00")) if taken_raw else None
            except Exception:
                taken_at = None
            media_id = row.get("id")
            items.append(SimpleNamespace(
                pk=media_id,
                code=code_match.group(1) if code_match else "",
                caption_text=row.get("caption", ""),
                taken_at=taken_at,
                like_count=row.get("like_count", 0),
                comment_count=row.get("comments_count", 0),
                play_count=self._fetch_reel_plays(str(media_id or "")),
            ))
        return items

    def media_comments(self, media_id: str, amount: int = 10) -> list:
        res = self._request(f"{media_id}/comments", {"fields": "id,text,username,timestamp", "limit": amount})
        return [
            SimpleNamespace(
                pk=c.get("id"),
                user_id=c.get("username", ""),
                user=SimpleNamespace(username=c.get("username", "")),
                text=c.get("text", ""),
                has_liked_comment=True,  # Graph API does not expose comment likes
            )
            for c in res.get("data", [])
        ]

    def media_comment(self, media_id: str, text: str):
        res = self._request(f"{media_id}/comments", {"message": text}, method="POST")
        return SimpleNamespace(pk=res.get("id"))

    def comment_pin(self, comment_pk: str):
        # Not exposed on Graph API; ignore cleanly so booster proceeds
        return None

    def comment_like(self, comment_pk: str):
        return None

    def clip_upload(self, path: Path, caption: str, thumbnail: Path | None = None):
        video_url = _derive_public_media_url(Path(path))
        if not video_url:
            raise RuntimeError("Official Graph API upload requires a repo-tracked file or PUBLIC_MEDIA_BASE_URL.")
        container_params = {
            "media_type": "REELS",
            "video_url": video_url,
            "caption": caption,
            "share_to_feed": "true",
        }
        if thumbnail:
            thumb_url = _derive_public_media_url(Path(thumbnail))
            if thumb_url:
                container_params["cover_url"] = thumb_url

        container = self._request(f"{self.user_id}/media", container_params, method="POST")
        cid = container["id"]
        status = None
        for _ in range(30):
            status = self._request(cid, {"fields": "status_code,status"}).get("status_code")
            if status == "FINISHED":
                break
            if status in ("ERROR", "EXPIRED"):
                raise RuntimeError(f"Graph API container {cid} failed with status={status}")
            time.sleep(5)
        if status != "FINISHED":
            raise RuntimeError(f"Graph API container {cid} timed out with status={status}")

        pub = self._request(f"{self.user_id}/media_publish", {"creation_id": cid}, method="POST")
        media_id = pub["id"]
        meta = self._request(media_id, {"fields": "id,permalink"})
        m = re.search(r"/(?:reel|p)/([^/]+)/", meta.get("permalink", ""))
        return SimpleNamespace(pk=media_id, code=m.group(1) if m else str(media_id))


def get_client(session_file=DEFAULT_SESSION_FILE, username=None, password=None, interactive: bool = True):
    """
    Initializes and authenticates the Instagram client.
    Automatically uses Meta Official Instagram Graph API when INSTA_GRAPH_ACCESS_TOKEN
    and INSTA_IG_USER_ID are configured, falling back to `instagrapi` session auth.
    """
    allow_prompt = interactive and sys.stdin.isatty()
    graph_token = os.environ.get("INSTA_GRAPH_ACCESS_TOKEN", "").strip()
    graph_uid = os.environ.get("INSTA_IG_USER_ID", "").strip()
    if graph_token and graph_uid:
        print("🏛️ Using Official Meta Instagram Graph API v21.0 (Zero-Ban Engine)!")
        return OfficialGraphClient(graph_token, graph_uid)
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
        except LoginRequired:
            print("⚠️ Saved session is expired (LoginRequired). Re-authenticating...")
        except Exception as e:
            if is_restriction_error(e):
                if not allow_prompt:
                    raise RuntimeError(f"❌ Instagram session blocked/challenged ({type(e).__name__}): {e}")
                print(f"⚠️ Instagram challenge/restriction detected ({type(e).__name__}: {e}). Re-authenticating...")
            elif getattr(cl, "user_id", None):
                print(f"⚠️ Timeline check warning ({e}), but session User ID {cl.user_id} is present. Proceeding with saved session.")
                session_loaded = True
                return cl
            else:
                print(f"⚠️ Saved session is expired or invalid ({e}). Re-authenticating...")

    # If session not loaded, authenticate with credentials
    uname = username or os.environ.get("INSTA_USERNAME")
    pword = password or os.environ.get("INSTA_PASSWORD")

    if not session_loaded and not (uname and pword):
        if not allow_prompt:
            raise RuntimeError(
                "❌ Instagram session is invalid or missing, and no credentials were provided.\n"
                "👉 Refresh local session with `python3 scripts/vynox_update_bio_and_dispatch.py --bio-only`, "
                "set INSTA_GRAPH_ACCESS_TOKEN + INSTA_IG_USER_ID, or update INSTA_SESSION_JSON in GitHub Secrets."
            )
        if not uname:
            uname = input("Instagram Username: ").strip()
        if not pword:
            pword = getpass.getpass("Instagram Password (hidden): ")

    print(f"🔄 Logging in as @{uname}...")
    try:
        cl.login(uname, pword)
    except TwoFactorRequired:
        if not allow_prompt:
            raise RuntimeError("❌ Two-Factor Authentication (2FA) required; cannot prompt in non-interactive mode.")
        print("🔐 Two-Factor Authentication (2FA) is enabled on this account.")
        code = input("Enter 2FA Code (from Authenticator App or SMS): ").strip()
        cl.login(uname, pword, verification_code=code)
    except ChallengeRequired:
        if not allow_prompt:
            raise RuntimeError("❌ Instagram security challenge required; resolve in official app and update INSTA_SESSION_JSON.")
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

    max_retries = 3
    media = None
    last_err = None

    for attempt in range(1, max_retries + 1):
        try:
            print(f"\n🚀 Uploading Reel (Attempt {attempt}/{max_retries}): {video_p.name} ({video_p.stat().st_size / (1024*1024):.2f} MB)...")
            print("⏳ Processing and optimizing on Instagram servers (this takes 15-40 seconds)...")
            media = cl.clip_upload(
                path=video_p,
                caption=caption,
                thumbnail=thumb_p
            )
            if media:
                break
        except Exception as e:
            last_err = e
            print(f"⚠️ Upload attempt {attempt} failed: {e}")
            if is_restriction_error(e):
                print("🛑 Stopping upload retries immediately due to account restriction/challenge/login error.")
                raise
            if attempt < max_retries:
                wait_s = attempt * 10
                print(f"⏳ Waiting {wait_s}s before retry...")
                time.sleep(wait_s)
    
    if not media:
        raise last_err

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
