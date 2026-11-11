#!/usr/bin/env python3
"""
Refresh @vynox_00000 Instagram session, update profile bio for the high-performing
2D Romantic Anime / Aesthetic Reel niche, and dispatch the next queued reel.
"""

import argparse
import subprocess
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

import daily_dispatcher
import insta_local_post

DEFAULT_USERNAME = "vynox_00000"
NEW_BIO = (
    "🌙 2D Anime & Lofi Lyric Stories\n"
    "🎧 Indie Songs • Late-Night Feels • Visual Art\n"
    "✨ New Aesthetic Reels Daily"
)


def sync_queue_to_remote() -> None:
    """Commits and pushes queue/archive state so GitHub Actions stays synchronized."""
    targets = [
        "projects/queue/",
        "projects/archive/",
        "projects/daily_dispatcher.log",
    ]
    if (BASE_DIR / "projects" / "duplicate_registry.json").exists():
        targets.append("projects/duplicate_registry.json")

    subprocess.run(["git", "add", *targets], cwd=str(BASE_DIR), check=False)
    diff = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=str(BASE_DIR),
        check=False,
    )
    if diff.returncode == 0:
        return

    subprocess.run(
        ["git", "commit", "-m", "chore: manual Reel dispatch sync [skip ci]"],
        cwd=str(BASE_DIR),
        check=True,
    )
    subprocess.run(
        ["git", "pull", "--rebase", "origin", "main"],
        cwd=str(BASE_DIR),
        check=False,
    )
    res = subprocess.run(
        ["git", "push", "origin", "main"],
        cwd=str(BASE_DIR),
        check=False,
    )
    if res.returncode == 0:
        print("✅ Queue and archive changes synced to origin/main.")
    else:
        print("⚠️ Could not push to origin/main automatically; please run 'git push origin main'.")


def update_bio(cl, biography: str) -> None:
    """Updates @vynox_00000 biography using Instagram's dedicated set_biography endpoint."""
    account = cl.account_info()
    print(f"👤 Connected Account: @{account.username} (ID: {account.pk})")
    print(f"📝 Current Bio:\n{account.biography}\n")

    if account.biography.strip() == biography.strip():
        print("✅ Bio is already up to date.")
        return

    ok = cl.account_set_biography(biography)
    if not ok:
        raise RuntimeError("Instagram returned non-ok status when updating biography.")

    refreshed = cl.account_info()
    print(f"✅ Bio successfully updated to:\n{refreshed.biography}\n")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Re-authenticate @vynox_00000, update bio, and dispatch next queued reel."
    )
    parser.add_argument(
        "--username",
        "-u",
        default=DEFAULT_USERNAME,
        help=f"Instagram username (default: {DEFAULT_USERNAME})",
    )
    parser.add_argument(
        "--bio-only",
        action="store_true",
        help="Only refresh login and update bio without dispatching a reel.",
    )
    args = parser.parse_args()

    cl = insta_local_post.get_client(username=args.username)
    update_bio(cl, NEW_BIO)

    if not args.bio_only:
        print("🚀 Dispatching next queued reel via daily_dispatcher...")
        daily_dispatcher.dispatch_next(force=True)
        sync_queue_to_remote()

    sess_path = insta_local_post.DEFAULT_SESSION_FILE
    print("\n" + "=" * 60)
    print("🔐 NEXT STEP — Sync Refreshed Session to GitHub Actions:")
    print("Run this command to copy Base64 session cleanly for secret INSTA_SESSION_JSON:")
    print(f"  base64 -w0 {sess_path}")
    print("Then paste it in GitHub -> Settings -> Secrets and variables -> Actions -> INSTA_SESSION_JSON")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    sys.exit(main())
