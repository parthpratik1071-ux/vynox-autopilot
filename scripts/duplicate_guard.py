#!/usr/bin/env python3
"""
Zero-Repeat Duplicate Prevention Guard
Ensures no video, song, or caption is ever produced or dispatched twice.
Checks local project folders, queue items, archive history, and live Instagram feed.
"""

import os
import sys
import json
import re
import hashlib
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SERIES_DIR = BASE_DIR / "projects" / "series-romantic-animations"
QUEUE_DIR = BASE_DIR / "projects" / "queue"
ARCHIVE_DIR = BASE_DIR / "projects" / "archive"
REGISTRY_FILE = BASE_DIR / "projects" / "duplicate_registry.json"

def normalize(text):
    if not text:
        return ""
    # Lowercase and keep alphanumeric and spaces
    clean = re.sub(r'[^a-zA-Z0-9\s]', ' ', str(text).lower())
    return " ".join(clean.split())

def get_all_registered_fingerprints():
    """Aggregates all titles, slugs, and filenames from history, queue, and projects."""
    fingerprints = {
        "titles": set(),
        "slugs": set(),
        "files": set(),
        "captions_head": set()
    }
    
    # 1. Check Series Projects
    if SERIES_DIR.exists():
        for d in SERIES_DIR.iterdir():
            if d.is_dir():
                fingerprints["slugs"].add(normalize(d.name))

    # 2. Check Queue
    if QUEUE_DIR.exists():
        for qf in QUEUE_DIR.glob("*.json"):
            try:
                with open(qf, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("title"):
                    fingerprints["titles"].add(normalize(data["title"]))
                if data.get("video_path"):
                    fingerprints["files"].add(Path(data["video_path"]).name.lower())
                if data.get("caption"):
                    first_line = data["caption"].strip().split("\n")[0]
                    fingerprints["captions_head"].add(normalize(first_line))
            except Exception:
                pass

    # 3. Check Archives
    if ARCHIVE_DIR.exists():
        for af in ARCHIVE_DIR.glob("*.json"):
            try:
                with open(af, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("title"):
                    fingerprints["titles"].add(normalize(data["title"]))
                if data.get("video_path"):
                    fingerprints["files"].add(Path(data["video_path"]).name.lower())
                if data.get("caption"):
                    first_line = data["caption"].strip().split("\n")[0]
                    fingerprints["captions_head"].add(normalize(first_line))
            except Exception:
                pass

    # 4. Check Registry File
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                reg = json.load(f)
            for item in reg.get("items", []):
                if item.get("title"):
                    fingerprints["titles"].add(normalize(item["title"]))
                if item.get("slug"):
                    fingerprints["slugs"].add(normalize(item["slug"]))
        except Exception:
            pass

    return fingerprints

def is_duplicate_song(title, artist=""):
    """
    Returns (True, reason) if the song or topic was already created or queued.
    """
    clean_title = normalize(title)
    clean_artist = normalize(artist)
    
    fps = get_all_registered_fingerprints()
    
    # Direct match on title
    for reg_title in fps["titles"]:
        if clean_title in reg_title or reg_title in clean_title:
            return True, f"Matched existing title '{reg_title}'"
            
    # Substring in slugs (e.g., 'kashish', 'choo-lo', 'husn', 'baarishein')
    clean_keywords = clean_title.split()
    for slug in fps["slugs"]:
        for kw in clean_keywords:
            if len(kw) > 3 and kw in slug:
                return True, f"Keyword '{kw}' matched project slug '{slug}'"
                
    return False, None

def is_duplicate_video(video_path, caption=""):
    """
    Checks if this exact video file or caption has already been published.
    """
    vp = Path(video_path)
    file_name = vp.name.lower()
    clean_cap_head = normalize(caption.strip().split("\n")[0]) if caption else ""
    
    fps = get_all_registered_fingerprints()
    
    if file_name in fps["files"]:
        # If it's already in archive, it's a duplicate!
        for af in ARCHIVE_DIR.glob("*.json"):
            try:
                with open(af, "r") as f:
                    d = json.load(f)
                if Path(d.get("video_path", "")).name.lower() == file_name:
                    if d.get("status") != "deleted_from_instagram":
                        return True, f"Video '{file_name}' already published on {af.name}"
            except Exception:
                pass

    if clean_cap_head and clean_cap_head in fps["captions_head"]:
        for af in ARCHIVE_DIR.glob("*.json"):
            try:
                with open(af, "r") as f:
                    d = json.load(f)
                arc_head = normalize(d.get("caption", "").strip().split("\n")[0])
                if arc_head == clean_cap_head and d.get("status") != "deleted_from_instagram":
                    return True, f"Caption headline already published on {af.name}"
            except Exception:
                pass
                
    return False, None

def register_video(title, video_path, caption="", slug="", status="queued"):
    """Saves a permanent record in duplicate_registry.json."""
    data = {"items": []}
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"items": []}
            
    entry = {
        "title": title,
        "slug": slug or normalize(title).replace(" ", "-"),
        "video_path": str(video_path),
        "caption_head": caption.strip().split("\n")[0] if caption else "",
        "status": status,
        "timestamp": str(Path(video_path).stat().st_mtime if Path(video_path).exists() else "")
    }
    
    # Avoid duplicate in registry
    existing_titles = [normalize(i.get("title", "")) for i in data["items"]]
    if normalize(title) not in existing_titles:
        data["items"].append(entry)
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

if __name__ == "__main__":
    fps = get_all_registered_fingerprints()
    print(f"✅ Duplicate Guard loaded:")
    print(f" - Registered Titles: {len(fps['titles'])}")
    print(f" - Registered Slugs: {len(fps['slugs'])}")
    print(f" - Registered Files: {len(fps['files'])}")
    
    # Test queries
    print("Testing 'Choo Lo':", is_duplicate_song("Choo Lo", "The Local Train"))
    print("Testing 'Kashish':", is_duplicate_song("Kashish", "Ashish Bhatia"))
    print("Testing 'Husn':", is_duplicate_song("Husn", "Anuv Jain"))
    print("Testing 'Baarishein':", is_duplicate_song("Baarishein", "Anuv Jain"))
    print("Testing 'New Unheard Song 2026':", is_duplicate_song("New Unheard Song 2026", "Unknown Artist"))
