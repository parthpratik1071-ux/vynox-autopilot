# 🤖 Vynox Autopilot — Multi-AI Coordination Handbook

> **Notice for Any AI Agent Working in This Workspace:**  
> This workspace operates with clear role boundaries to ensure zero conflicts, 100% queue safety, and deterministic publishing.

---

## 1. Division of Responsibilities

| Role | Agent / Responsibility | What It Handles |
|---|---|---|
| **Backend & Infrastructure Agent** *(This Agent)* | **Code & Automation** | Instagram & YouTube APIs, GitHub Actions CI/CD, queue dispatcher, duplicate guard, scheduling crons, session health, test suites. |
| **Creative / Director Agent** *(Other Chats/AIs)* | **Art & Video Production** | Storyboarding, Midjourney/Gemini image prompts, voiceovers, lyrics synchronization, rendering `.mp4` video files. |

---

## 2. Connected Channels & Live Status

* **Instagram:** `@vynox_00000` (Account ID: `16183885323`)
  * Local Session: `~/.config/stickman_video_director/insta_session.json`
  * Status: **`HEALTHY (SESSION_VALID)`**
* **YouTube:** `_void_X` (4 subscribers)
  * Token: `~/.config/stickman_video_director/youtube_token.json`
  * API: YouTube Data API v3 (Project `678106304004`)
  * Status: **`HEALTHY (YOUTUBE_AUTH_HEALTHY)`**

---

## 3. How to Queue a New Video for Automated Publishing

When a creative AI finishes rendering a new video, stage it into `projects/queue/`:

### File Path & Video Format
1. Render vertical **9:16** MP4 (`1080x1920@30fps`, loudness normalized `-10` to `-15 dB`, duration **under 60s** for YouTube Shorts compatibility).
2. Save video in:
   ```text
   projects/series-romantic-animations/<series-folder>/output/film_<name>.mp4
   ```
3. Save cover/thumbnail in:
   ```text
   projects/series-romantic-animations/<series-folder>/output/cover.jpg
   ```

### Queue JSON Schema
Create a file named `projects/queue/<idx>_<slug>.json` (e.g., `10_romantic_ishq.json`):

```json
{
  "title": "Ishq - 2D Winter Romance",
  "song_title": "Ishq",
  "artist": "Faheem Abdullah & Rauhan Malik",
  "video_path": "projects/series-romantic-animations/09-ishq-faheem/output/film_ishq.mp4",
  "cover_path": "projects/series-romantic-animations/09-ishq-faheem/output/cover.jpg",
  "caption": "Ye ishq nahi aasan... ek aag ka dariya hai. 🏔️❄️✨\n\nMisty pine valleys and a love that weathers every cold storm. 🤍\n\nArt & Animation: @vynox_00000\nSong: Ishq • Faheem Abdullah\n\n#ishq #faheemabdullah #2danimation #lovesongs #aestheticreels #reelsindia #Shorts"
}
```

---

## 4. Automated Publishing Schedule

GitHub Actions (`.github/workflows/daily_reel.yml`) automatically dispatches the next queued item twice daily during peak audience activity:

* **Slot 1 (Evening):** **7:30 PM IST** (`14:00 UTC`)
* **Slot 2 (Late-Night Viral Peak):** **9:45 PM IST** (`16:15 UTC`)

### Dual-Posting Rule
Every scheduled run automatically uploads to:
1. **Instagram Reels** (`@vynox_00000`)
2. **YouTube Shorts** (`_void_X`) with YouTube **Synthetic/AI Content Disclosure** automatically injected.

---

## 5. Duplicate Guard (Zero-Repeat Shield)

Before starting work on a song, run:
```bash
python3 -c "import duplicate_guard; print(duplicate_guard.is_duplicate_song('<Song Name>', '<Artist>'))"
```
Or scan trending candidate topics:
```bash
python3 scripts/trending_radar.py --scan
```
Check `projects/trending_report.md` for live fresh candidates across YouTube and Instagram.

---

## 6. Key Commands for Any AI Agent

```bash
# 1. Verify all authentication
python3 scripts/insta_local_post.py --check-auth
python3 scripts/youtube_uploader.py --check-auth

# 2. Run multi-platform trending scanner
python3 scripts/trending_radar.py --scan

# 3. Test queue dispatcher (dry-run/simulation)
python3 scripts/daily_dispatcher.py

# 4. Run automated test suite (must pass 19/19 tests)
python3 -m unittest discover -s tests -v
```

