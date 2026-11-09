#!/usr/bin/env python3
"""
NexoraAI Emergency Alert Engine
Monitors DMs for high-priority emergency signals:
- Keywords: 'urgent', 'call utha', 'emergency', 'jaldi phone kar', 'hospital', etc.
- Multiple missed video/audio calls in a single burst
Sends instant notifications to Telegram / Webhook and logs to projects/emergency_alerts.log.
"""

import os
import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
ALERT_LOG = BASE_DIR / "projects" / "emergency_alerts.log"
ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)

URGENT_KEYWORDS = [
    "urgent", "emergency", "call utha", "phone utha", "uthana",
    "jaldi call", "urgent hai", "mar gaya", "hospital", "accident",
    "bhai call kar", "please utha", "zaruri hai", "kaha mar gaya", "plz call"
]

class EmergencyAlerter:
    def __init__(self):
        self.bot_token = os.environ.get("TELEGRAM_ALERT_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.environ.get("TELEGRAM_ALERT_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
        self.webhook_url = os.environ.get("EMERGENCY_WEBHOOK_URL")

    def check_for_emergency(self, sender_username: str, messages: list) -> bool:
        """
        Inspects message burst for emergency cues.
        """
        call_count = sum(1 for m in messages if "call" in str(getattr(m, "item_type", "")).lower())
        texts = [getattr(m, "text", "") or "" for m in messages]
        combined_text = " ".join(texts).lower()

        is_emergency = False
        reasons = []

        if call_count >= 2:
            is_emergency = True
            reasons.append(f"{call_count} missed calls")

        for kw in URGENT_KEYWORDS:
            if kw in combined_text:
                is_emergency = True
                reasons.append(f"urgent keyword: '{kw}'")
                break

        if is_emergency:
            reason_str = ", ".join(reasons)
            preview = combined_text[:120] if combined_text else "[Calls only]"
            self.send_alert(sender_username, reason_str, preview)
            return True

        return False

    def send_alert(self, sender: str, reason: str, preview: str):
        IST = timezone(timedelta(hours=5, minutes=30))
        now_str = datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p IST')
        log_entry = f"[{now_str}] 🚨 ALERT from @{sender} | Reason: {reason} | Text: \"{preview}\"\n"

        # 1. Log locally to projects/emergency_alerts.log
        try:
            with open(ALERT_LOG, "a", encoding="utf-8") as f:
                f.write(log_entry)
            print(f"🚨 [EMERGENCY-ALERT] Logged alert for @{sender}: {reason}")
        except Exception as e:
            print(f"⚠️ Failed to write alert log: {e}")

        # 2. Telegram Alert (if configured)
        if self.bot_token and self.chat_id:
            try:
                msg = (
                    f"🚨 *URGENT INSTAGRAM DM ALERT*\n\n"
                    f"👤 *From:* @{sender}\n"
                    f"⚠️ *Detected:* {reason}\n"
                    f"💬 *Message:* _{preview}_\n"
                    f"⏰ *Time:* {now_str}\n\n"
                    f"👉 _Check Instagram DMs immediately!_"
                )
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = urllib.parse.urlencode({
                    "chat_id": self.chat_id,
                    "text": msg,
                    "parse_mode": "Markdown"
                }).encode("utf-8")
                req = urllib.request.Request(url, data=data)
                with urllib.request.urlopen(req, timeout=5) as resp:
                    if resp.status == 200:
                        print(f"📲 Telegram emergency alert dispatched to chat {self.chat_id}")
            except Exception as e:
                print(f"⚠️ Could not dispatch Telegram alert: {e}")

        # 3. Webhook Alert (if configured)
        if self.webhook_url:
            try:
                payload = json.dumps({
                    "event": "instagram_emergency",
                    "sender": sender,
                    "reason": reason,
                    "preview": preview,
                    "timestamp": now_str
                }).encode("utf-8")
                req = urllib.request.Request(self.webhook_url, data=payload, headers={"Content-Type": "application/json"})
                urllib.request.urlopen(req, timeout=5)
            except Exception:
                pass

alerter = EmergencyAlerter()
