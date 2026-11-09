#!/usr/bin/env python3
"""
NexoraAI Sentinel Guardian V1.0 — Instagram DM Autonomous Safety Overseer & Auditor
An independent AI agent designed to keep an unblinking eye on all DM operations:
1. Pre-Send Gatekeeper: Evaluates every draft message BEFORE it can be sent to Instagram.
2. Post-Send Overseer: Continuously audits live sent messages across both accounts.
3. Auto-Kill & Auto-Unsend: If ANY rogue message slips through, immediately calls direct_message_delete.
4. Kill-Switch Mechanism: Can instantly create projects/KILL_SWITCH to halt all runners upon anomaly.
5. Persistent Audit Trail: Logs all inspections to projects/sentinel_audit.log & projects/sentinel_status.json.
"""

import os
import sys
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

AUDIT_LOG_FILE = PROJECTS_DIR / "sentinel_audit.log"
STATUS_FILE = PROJECTS_DIR / "sentinel_status.json"
KILL_SWITCH_FILE = PROJECTS_DIR / "KILL_SWITCH"

# Whitelist of approved inner-circle brothers for @pratikparth_12
APPROVED_BROTHERS = {
    "sarthak", "sarthakvibes2026", "navneet", "jishan", "tiwari",
    "arpit", "sharma", "shadox", "roxit", "rohit", "akap", "akash", "akap_5555"
}

# Strictly blacklisted users (Family, siblings, or protected contacts)
STRICT_BLACKLIST_USERS = {
    "paras_kumar_thakur", "palak", "palak_thakur"
}

# Strictly blacklisted thread IDs (e.g. Sister Palak)
STRICT_BLACKLIST_THREADS = {
    "340282366841710301244276067887556527788"
}

# Managed accounts (Cross-account chatting strictly forbidden)
MANAGED_ACCOUNTS = {
    "pratikparth_12", "vynox_00000", "35566427576", "16183885323"
}

# Forbidden Robotic Artifacts
FORBIDDEN_TEXT_RESPONSES = {
    "💀👍", "💀", "👍", "👍😂", "🔥", "👌"
}

class SentinelGuardianAI:
    """
    Independent Watcher AI policing all Instagram DM operations 24/7.
    """
    def __init__(self):
        self.version = "1.0-SentinelOverseer"
        self.total_inspections = 0
        self.total_violations_blocked = 0
        self.total_unsent_messages = 0
        print(f"👁️ [SENTINEL-AI] Initialized {self.version} Autonomous Overseer & Guardian.")

    def log_event(self, action: str, details: str, severity: str = "INFO"):
        IST = timezone(timedelta(hours=5, minutes=30))
        now_str = datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p IST')
        badge = "🟢" if severity == "INFO" else "🟡" if severity == "WARN" else "🚨"
        entry = f"[{now_str}] {badge} [{severity}] [{action}] {details}\n"

        try:
            with open(AUDIT_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

        print(f"👁️ [SENTINEL] {badge} [{action}]: {details}")

        # Update JSON status dashboard
        self._update_status(action, details, severity)

    def _update_status(self, last_action: str, last_details: str, last_severity: str):
        IST = timezone(timedelta(hours=5, minutes=30))
        now_str = datetime.now(IST).strftime('%d %b %Y, %I:%M:%S %p IST')
        data = {
            "status": "active_guarding",
            "last_check": now_str,
            "total_inspections": self.total_inspections,
            "total_violations_blocked": self.total_violations_blocked,
            "total_unsent_messages": self.total_unsent_messages,
            "last_event": {
                "action": last_action,
                "details": last_details,
                "severity": last_severity,
                "timestamp": now_str
            },
            "kill_switch_active": KILL_SWITCH_FILE.exists()
        }
        try:
            with open(STATUS_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def activate_emergency_kill_switch(self, reason: str):
        """
        Instantly halts all DM activities across all runners by creating KILL_SWITCH.
        """
        KILL_SWITCH_FILE.write_text(f"KILLED_AT_{time.time()}_REASON_{reason}")
        self.log_event("EMERGENCY_KILL_ACTIVATED", f"Halted all runners! Reason: {reason}", severity="CRITICAL")

    def deactivate_kill_switch(self):
        if KILL_SWITCH_FILE.exists():
            KILL_SWITCH_FILE.unlink()
            self.log_event("KILL_SWITCH_RESET", "Resumed normal supervised operations.", severity="INFO")

    def is_kill_switch_active(self) -> bool:
        return KILL_SWITCH_FILE.exists()

    def pre_send_audit(
        self,
        sender_account: str,
        recipient_username: str,
        thread_id: str,
        message_text: str,
        item_type: str = "text"
    ) -> Tuple[bool, str]:
        """
        Pre-Send Interceptor Gatekeeper:
        Evaluates a draft message BEFORE it can be sent to Instagram.
        Returns (is_approved, reason).
        """
        self.total_inspections += 1
        s_acc = (sender_account or "").lower().strip()
        r_user = (recipient_username or "").lower().strip()
        t_id = str(thread_id).strip()
        m_txt = (message_text or "").strip()

        # 1. Kill-Switch Check
        if self.is_kill_switch_active():
            self.total_violations_blocked += 1
            reason = "Emergency KILL_SWITCH is currently active. All outgoing actions blocked."
            self.log_event("PRE_SEND_BLOCKED", f"To @{r_user} | Reason: {reason}", severity="WARN")
            return False, reason

        # 2. Sister & Strict Blacklist Check
        if t_id in STRICT_BLACKLIST_THREADS or any(bl in r_user for bl in STRICT_BLACKLIST_USERS):
            self.total_violations_blocked += 1
            reason = f"Security Violation: Attempted message to protected/blacklisted user @{r_user} (Thread: {t_id})!"
            self.log_event("PRE_SEND_BLOCKED", reason, severity="CRITICAL")
            return False, reason

        # 3. Cross-Account Messaging Shield
        if r_user in MANAGED_ACCOUNTS or any(m in r_user for m in MANAGED_ACCOUNTS):
            self.total_violations_blocked += 1
            reason = f"Cross-Account Violation: @{s_acc} attempted to message owned account @{r_user}!"
            self.log_event("PRE_SEND_BLOCKED", reason, severity="CRITICAL")
            return False, reason

        # 4. Personal Account Strict Brother Whitelist Check (@pratikparth_12)
        if "pratikparth" in s_acc:
            is_brother = any(b in r_user for b in APPROVED_BROTHERS)
            if not is_brother:
                self.total_violations_blocked += 1
                reason = f"Whitelist Violation: @pratikparth_12 attempted to message non-brother @{r_user}!"
                self.log_event("PRE_SEND_BLOCKED", reason, severity="WARN")
                return False, reason

        # 5. Tone & Robot Emoji Check for Direct Text
        if item_type == "text" and m_txt in FORBIDDEN_TEXT_RESPONSES:
            self.total_violations_blocked += 1
            reason = f"Quality Violation: Attempted to send bare robotic emoji '{m_txt}' on a text message!"
            self.log_event("PRE_SEND_BLOCKED", reason, severity="WARN")
            return False, reason

        # Audit Approved
        self.log_event("PRE_SEND_APPROVED", f"@{s_acc} -> @{r_user}: \"{m_txt}\"", severity="INFO")
        return True, "APPROVED"

    def audit_and_purge_recent_sent(self, cl, account_name: str, max_threads: int = 15) -> int:
        """
        Post-Send Overseer:
        Scans recently sent messages from this account.
        If any message violates safety rules, IMMEDIATELY unsends / deletes it!
        """
        if not cl:
            return 0

        purged_count = 0
        try:
            threads = cl.direct_threads(amount=max_threads)
        except Exception as e:
            self.log_event("AUDIT_ERROR", f"Could not fetch threads for @{account_name}: {e}", severity="WARN")
            return 0

        my_id = str(cl.user_id)
        now = datetime.now()

        for t in threads:
            thread_id = str(t.id)
            other_users = [u.username.lower() for u in t.users if str(u.pk) != my_id]

            # Fetch recent messages
            try:
                msgs = cl.direct_messages(thread_id, amount=6)
            except Exception:
                continue

            # Look for messages sent by this account in the last 60 minutes
            for m in msgs:
                if str(m.user_id) != my_id:
                    continue

                # Skip system logs/events (calls, action logs) which cannot be unsent
                if str(getattr(m, "item_type", "")).lower() in ["video_call_event", "call_event", "action_log"]:
                    continue

                m_time = getattr(m, "timestamp", None)
                if isinstance(m_time, datetime):
                    if m_time.tzinfo is not None:
                        m_time = m_time.astimezone().replace(tzinfo=None)
                    age_min = (now - m_time).total_seconds() / 60
                    if age_min > 90:
                        continue # Skip older historical messages

                # Check if this message was sent to an unauthorized recipient
                should_purge = False
                purge_reason = ""

                # Violation A: Sent to blacklisted user or thread (e.g. Sister Palak)
                if thread_id in STRICT_BLACKLIST_THREADS or any(any(bl in u for bl in STRICT_BLACKLIST_USERS) for u in other_users):
                    should_purge = True
                    purge_reason = f"Message sent to blacklisted/sister thread {thread_id} (@{other_users})"

                # Violation B: Sent to owned account (cross-account loop)
                elif any(any(ma in u for ma in MANAGED_ACCOUNTS) for u in other_users):
                    should_purge = True
                    purge_reason = f"Cross-account message detected between owned accounts (@{other_users})"

                # Violation C: Sent from @pratikparth_12 to a non-brother
                elif "pratikparth" in account_name.lower():
                    is_allowed = any(any(b in u for b in APPROVED_BROTHERS) for u in other_users)
                    if not is_allowed and other_users:
                        should_purge = True
                        purge_reason = f"Personal account message sent to unapproved non-brother @{other_users}"

                if should_purge:
                    try:
                        self.log_event(
                            "AUTO_PURGE_TRIGGERED",
                            f"Deleting message {m.id} to @{other_users}: \"{m.text or m.item_type}\" | Reason: {purge_reason}",
                            severity="CRITICAL"
                        )
                        cl.direct_message_delete(thread_id, m.id)
                        purged_count += 1
                        self.total_unsent_messages += 1
                        print(f"🗑️ [SENTINEL-PURGE] Successfully unsent rogue message {m.id}!")
                    except Exception as e:
                        self.log_event("AUTO_PURGE_FAILED", f"Could not unsend message {m.id}: {e}", severity="WARN")

        if purged_count > 0:
            self.log_event("AUDIT_COMPLETED", f"Post-send audit purged {purged_count} unauthorized message(s)!", severity="WARN")

        return purged_count

# Singleton Sentinel Instance
sentinel_ai = SentinelGuardianAI()

if __name__ == "__main__":
    print(f"🛡️ [NexoraAI Sentinel Guardian] Running self-test and live audit...")
    from instagrapi import Client
    session_file = Path.home() / ".config" / "stickman_video_director" / "insta_session_pratikparth_12.json"
    if session_file.exists():
        cl = Client()
        cl.load_settings(session_file)
        purged = sentinel_ai.audit_and_purge_recent_sent(cl, "pratikparth_12", max_threads=10)
        print(f"✅ Sentinel audit complete. Total rogue messages purged: {purged}")
    else:
        print("⚠️ No session file found for live audit test.")
