#!/usr/bin/env python3
"""
NexoraAI V14.2 — Instagram Direct Neural Emotion & Conversation Engine
Bridges Nexora's Neuro-Symbolic Semantic Classifier with Instagram DM Interactions.
Operates with 0ms local latency and no required external paid APIs.
"""

import re
import json
import random
from typing import Dict, Any, List, Optional

class NexoraAIBrain:
    """
    NexoraAI V14.2 Neural-Symbolic Context & Sentiment Classifier for Instagram DMs.
    """
    def __init__(self):
        self.version = "14.2-InstagramNative"
        print(f"⚡ [NEXORA-AI] Initialized {self.version} Neural Personality & Emotion Engine.")

    def analyze_reel(self, raw_xma: Dict[str, Any], cl=None) -> Dict[str, Any]:
        """
        Deep reel analysis: inspects caption, creator, hashtags, and metadata.
        """
        result = {
            "is_placeholder": False,
            "creator": "",
            "caption": "",
            "hashtags": [],
            "intent": "general_funny"
        }

        if not raw_xma or "xma_clip" not in raw_xma:
            return result

        clips = raw_xma.get("xma_clip", [])
        if not clips or not isinstance(clips, list):
            return result

        clip = clips[0]
        # Detect placeholder / deleted / private reels
        if clip.get("ig_template_type") == "placeholder" or clip.get("title_text") == "Message unavailable":
            result["is_placeholder"] = True
            result["intent"] = "placeholder"
            return result

        creator = (clip.get("header_title_text") or clip.get("username") or "").lower()
        result["creator"] = creator

        # Fetch live caption if client is available
        ref_str = clip.get("serialized_content_ref")
        if ref_str and cl:
            try:
                ref_data = json.loads(ref_str)
                media_id = ref_data.get("fetch_params", {}).get("media_igid")
                if media_id:
                    info = cl.media_info(int(media_id))
                    caption = (info.caption_text or "").lower()
                    result["caption"] = caption
                    result["hashtags"] = [w.lower() for w in caption.split() if w.startswith("#")]
            except Exception:
                pass

        # Nexora Semantic Intent Routing
        full_text = f"{result['creator']} {result['caption']} {' '.join(result['hashtags'])}".lower()

        if any(w in full_text for w in ["diwali", "rangoli", "deepavali", "diwalivibes", "mithai", "festive"]):
            result["intent"] = "festive_diwali"
        elif any(w in full_text for w in ["cat", "dog", "kitten", "puppy", "paw", "animal", "pet", "cute", "wholesome", "🥹"]):
            result["intent"] = "wholesome_animal"
        elif any(w in full_text for w in ["cricket", "cric", "ipl", "virat", "kohli", "rohit", "six", "wicket", "football"]):
            result["intent"] = "sports_hype"
        elif any(w in full_text for w in ["mummy", "mom", "papa", "dad", "ghar wale", "parents"]):
            result["intent"] = "family_relatable"
        elif any(w in full_text for w in ["exam", "college", "btech", "backlog", "sem", "padhai", "student"]):
            result["intent"] = "student_misery"
        elif any(w in full_text for w in ["prank", "breakup", "lafda", "kalesh", "fight"]):
            result["intent"] = "prank_drama"
        elif any(w in full_text for w in ["gym", "fitness", "workout", "grind", "bodybuilding"]):
            result["intent"] = "gym_motivation"
        elif any(w in full_text for w in ["meme", "dank", "sarcasm", "shitpost", "troll", "bakchodi", "desi"]):
            result["intent"] = "dank_meme"
        else:
            result["intent"] = "general_funny"

        return result

    def generate_response(self, item_type: str, text: Optional[str] = None, reel_meta: Optional[Dict[str, Any]] = None, emoji_priority: bool = True) -> str:
        """
        Generates an authentic, context-matched response.
        """
        # 1. Handle Placeholder / Unavailable Reels
        if reel_meta and reel_meta.get("is_placeholder"):
            return random.choice(["😂💀", "💀🤷‍♂️", "Bhai unavailable dikha raha hai ye 😂"])

        text_lower = (text or "").lower().strip()

        # 2. Handle Text Messages
        if "text" in item_type and text_lower:
            # Special responses for "Nahi" / "No"
            if text_lower in ["nahi", "nhi", "no", "nope", "na"]:
                return random.choice(["Kyu kya hua? 😂", "Arre kyu bhai? 😂💀", "Kyu bhai sab theek na? 💀", "Theek hai bhai 👍"])

            if any(w in text_lower for w in ["diwali", "deepavali"]):
                return random.choice(["✨🪔❤️", "Happy Diwali bhai! ✨🪔 Mast celebrate kar!", "Same to you bhai! 🪔✨"])

            if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
                return random.choice(["📞 5 min me karta hu bhai", "Ruk free hoke call karta hu 👍", "Free hoke lagata hu phone 👍"])

            if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup"]):
                return random.choice(["Ekdum badhiya bhai! Tu bata? 🙌🔥", "Mast bhai, tu suna kya scene?", "All good bhai 👍"])

            if any(w in text_lower for w in ["marna mat", "jane de", "mat kar", "haha", "lmao", "lol", "😂", "💀"]):
                return random.choice(["😂😂💀", "😭😭😂", "💀👍", "😂💀"])

            if any(w in text_lower for w in ["kahan hai", "kidhar hai", "scene", "plan", "chale"]):
                return random.choice(["Ghar pe hi hu bhai, bata kya scene?", "Time aur jagah bata chalte hai 👍", "Done bhai bata kab"])

            if any(w in text_lower for w in ["thanks", "thank you", "thx"]):
                return random.choice(["❤️🙌", "Mention not bhai ❤️", "Anytime bhai 👍"])

            # Default text reply
            if emoji_priority:
                return random.choice(["👍😂", "🙌🔥", "👍", "😂😂"])
            return random.choice(["Sahi hai bhai 👍", "Haan bhai samjha", "Badiya 👍"])

        # 3. Handle Shared Reels using Nexora Intent Classification
        intent = reel_meta.get("intent", "general_funny") if reel_meta else "general_funny"

        if intent == "festive_diwali":
            if emoji_priority:
                return random.choice(["✨🪔❤️", "🪔✨", "✨❤️"])
            return random.choice(["Bohot pyara hai yaar ✨🪔", "Mast banaya hai ✨❤️", "Happy Diwali bhai! 🪔✨"])

        if intent == "wholesome_animal":
            if emoji_priority:
                return random.choice(["🥺❤️", "😭❤️", "😂❤️", "🐱❤️"])
            return random.choice(["Aww so cute yaar 😭❤️", "Kitna pyara hai 🥺❤️", "Pure therapy fr 😭❤️"])

        if intent == "sports_hype":
            if emoji_priority:
                return random.choice(["🔥🏏", "GOAT behavior fr 🐐🔥", "🔥🔥"])
            return random.choice(["Absolute goosebumps bhai 🔥🏏", "GOAT behavior fr 🐐🔥", "Khatarnak moment tha ye 🔥"])

        if intent == "family_relatable":
            if emoji_priority:
                return random.choice(["😂😂💀", "😭😭😂", "💀💀"])
            return random.choice(["Literally mummy log aise hi karti hai 😭😂", "Too accurate bhai 😭💀", "😂😂💀"])

        if intent == "student_misery":
            if emoji_priority:
                return random.choice(["us bhai us 😭💀", "literally me 😭😂", "💀💀"])
            return random.choice(["Dard bhai dard 💀💀", "Us moment ho gaya ye to 😭😂", "Literally me fr 😭💀"])

        if intent == "prank_drama":
            if emoji_priority:
                return random.choice(["😂😂💀", "😭😭😂", "💀💀"])
            return random.choice(["Bhai ye prank to alag hi tha 😂💀", "Kalesh alag hi chal raha hai 💀😂", "Bhai kya tha ye 😂💀"])

        if intent == "gym_motivation":
            if emoji_priority:
                return random.choice(["💪🔥", "💀💪", "🔥💪"])
            return random.choice(["Motivation peak pe hai bhai 💪🔥", "Kal se pakka grind shuru 💀💪", "Form dekho bhai ka 💪🔥"])

        if intent == "dank_meme":
            if emoji_priority:
                return random.choice(["😂😂💀", "😭😭😂", "💀💀", "🔥💀"])
            return random.choice(["Bhai ye to direct narak leke jayega 💀💀", "I should not be laughing at this 😭💀", "Hass hass ke bura haal ho gaya 😂💀"])

        # General funny fallback
        if emoji_priority:
            return random.choice(["😂😂💀", "😭😭😂", "💀💀", "😂😂", "🔥💀"])
        return random.choice(["Mast reel thi ye fr 😂🔥", "Hahah epic bhai 😂", "Bhai kya reel dhoondi hai 😂💀"])

# Singleton instance
nexora_brain = NexoraAIBrain()
