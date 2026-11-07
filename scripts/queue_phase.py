#!/usr/bin/env python3
"""
Vynox Autopilot: Phase & Occasion Calendar Manager
Inspects, validates, and manages the 4 production phases (60 Reels) for the 30-day master plan.
"""

import sys
import json
import argparse
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
PHASES_DIR = BASE_DIR / "projects" / "phases"
QUEUE_DIR = BASE_DIR / "projects" / "queue"
ARCHIVE_DIR = BASE_DIR / "projects" / "archive"

PHASE_FILES = {
    1: PHASES_DIR / "phase_1_diwali_cosmic.json",
    2: PHASES_DIR / "phase_2_childhood_devotion.json",
    3: PHASES_DIR / "phase_3_popculture_justice.json",
    4: PHASES_DIR / "phase_4_winter_defence.json"
}

def load_phase(phase_num):
    p = PHASE_FILES.get(phase_num)
    if not p or not p.exists():
        print(f"❌ Phase {phase_num} file not found at {p}")
        return None
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def list_phases():
    print("=" * 70)
    print("🎬 VYNOX AUTOPILOT: 30-DAY OCCASION & FESTIVAL MASTER ROADMAP")
    print("=" * 70)
    total_reels = 0
    for num in sorted(PHASE_FILES.keys()):
        data = load_phase(num)
        if not data:
            continue
        count = len(data.get("reels", []))
        total_reels += count
        print(f"📍 Phase {data.get('phase')}: {data.get('name')}")
        print(f"   📅 Dates: {data.get('dates')} | 🎞️ Reels: {count}")
        print(f"   📝 Summary: {data.get('description')}")
        print("-" * 70)
    print(f"✨ Total Scheduled Reels Across 4 Phases: {total_reels} (60 Target)")
    print("=" * 70)

def show_phase(phase_num):
    data = load_phase(phase_num)
    if not data:
        return
    print("\n" + "=" * 80)
    print(f"📍 PHASE {data.get('phase')}: {data.get('name').upper()} ({data.get('dates')})")
    print(f"📝 {data.get('description')}")
    print("=" * 80)
    for r in data.get("reels", []):
        day = r.get("day")
        date = r.get("date")
        slot = r.get("slot")
        occ = r.get("occasion")
        title = r.get("title")
        style = r.get("style")
        hook = r.get("hook")
        print(f" Day {day:02d} | {date} | {slot:<12} | 🏷️ {occ}")
        print(f"    🎬 Title: {title}")
        print(f"    🎨 Style: {style}")
        print(f"    🪝 Hook: \"{hook}\"")
        print("-" * 80)

def main():
    parser = argparse.ArgumentParser(description="Vynox 4-Phase Content Calendar Manager")
    parser.add_argument("--list", action="store_true", help="List summary of all 4 phases")
    parser.add_argument("--phase", type=int, choices=[1, 2, 3, 4], help="Show detailed breakdown of a specific phase (1-4)")
    args = parser.parse_args()

    if args.phase:
        show_phase(args.phase)
    else:
        list_phases()

if __name__ == "__main__":
    main()
