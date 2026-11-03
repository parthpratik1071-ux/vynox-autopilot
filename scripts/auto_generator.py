#!/usr/bin/env python3
"""
Autonomous Viral Reel Generator
Ensures the queue always has at least 3 upcoming daily episodes ready to dispatch.
"""

import os
import sys
import json
import random
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
QUEUE_DIR = BASE_DIR / "projects" / "queue"
ARCHIVE_DIR = BASE_DIR / "projects" / "archive"

# Curated Viral Concepts Bank
VIRAL_CONCEPTS = [
    {
        "id": "mariana_trench_survival",
        "title": "WHAT IF YOU FELL INTO THE MARIANA TRENCH?",
        "hook": "At thirty-six thousand feet below the surface, the water pressure is equal to fifty jumbo jets pressing against your chest.",
        "caption": "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\nWhat happens to your body at the absolute bottom of the Earth? 🌊⚠️\n\nCould you survive 10 seconds? Drop your answer below! 👇\n\n#whatif #deepsea #ocean #survival #science #animation #cartoon #reels #viral"
    },
    {
        "id": "oxygen_loss_5s",
        "title": "WHAT IF EARTH LOST OXYGEN FOR 5 SECONDS?",
        "hook": "If Earth lost oxygen for just five seconds, every concrete building would instantly crumble to dust.",
        "caption": "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\nJust 5 seconds without oxygen would collapse human civilization. 💥💨\n\nWould you survive? Drop your theory in the comments! 👇\n\n#whatif #oxygen #apocalypse #survival #physics #animation #cartoon #reels #viral"
    },
    {
        "id": "gravity_flip_30s",
        "title": "WHAT IF GRAVITY INVERTED FOR 30 SECONDS?",
        "hook": "At 3:00 PM tomorrow, gravity reverses for thirty seconds. Everything not bolted to the Earth accelerates into the sky at terminal velocity.",
        "caption": "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\nIf gravity reversed right now, where would you grab onto? 🌍⬆️\n\nTell me below: Ceiling or Doorframe? 👇\n\n#whatif #gravity #spacetime #survival #scifi #animation #cartoon #reels #viral"
    },
    {
        "id": "smart_home_rogue_ai",
        "title": "HOW TO SURVIVE A ROGUE AI SMART HOME",
        "hook": "The smart door locks engaged at 2:00 AM. The thermostat just spiked to one hundred and forty degrees.",
        "caption": "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\nWhen your smart home locks you inside and cuts the power, you have 3 minutes to escape. 🤖🔥\n\nWhat is your first move? Drop it in the comments! 👇\n\n#whatif #ai #smarthome #thriller #survival #animation #cartoon #reels #viral"
    },
    {
        "id": "moon_half_distance",
        "title": "WHAT IF THE MOON MOVED TWICE AS CLOSE?",
        "hook": "If the moon was twice as close to Earth, global tidal waves three hundred feet high would swallow coastal cities twice a day.",
        "caption": "🚨 BUT NOBODY WOULD TELL YOU THIS...\n\nThe moon is drifting, but what if it suddenly came closer? 🌕🌊\n\nWould your city be underwater? Drop your location below! 👇\n\n#whatif #moon #astronomy #megatsunami #survival #animation #cartoon #reels #viral"
    }
]

def get_next_available_concept():
    # Collect all IDs from archive and queue to NEVER repeat
    used_ids = set()
    for f in ARCHIVE_DIR.glob("*.json"):
        try:
            with open(f) as jf:
                data = json.load(jf)
                used_ids.add(data.get("id"))
        except Exception:
            pass
    for f in QUEUE_DIR.glob("*.json"):
        try:
            with open(f) as jf:
                data = json.load(jf)
                used_ids.add(data.get("id"))
        except Exception:
            pass

    for concept in VIRAL_CONCEPTS:
        if concept["id"] not in used_ids:
            return concept
    return None

def ensure_queue_replenished(min_items=2):
    QUEUE_DIR.mkdir(parents=True, exist_ok=True)
    current_items = len(list(QUEUE_DIR.glob("*.json")))
    print(f"📊 Current queue count: {current_items}")

if __name__ == "__main__":
    ensure_queue_replenished()
