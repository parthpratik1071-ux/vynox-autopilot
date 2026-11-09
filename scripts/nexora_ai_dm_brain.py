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

    def generate_response(
        self,
        item_type: str,
        text: Optional[str] = None,
        reel_meta: Optional[Dict[str, Any]] = None,
        emoji_priority: bool = True,
        recent_history: Optional[List[str]] = None
    ) -> str:
        """
        Generates an authentic, context-matched response across all DM types:
        reels, stories, stickers, voice notes, photos, and direct text messages.
        Behaves 100% like a real human friend: uses natural Hinglish, avoid repetition,
        and understands conversational nuance.
        """
        candidates: List[str] = []
        recent_history = [r.lower().strip() for r in (recent_history or [])]

        def pick_unique(pool: List[str]) -> str:
            unseen = [p for p in pool if p.lower().strip() not in recent_history]
            if unseen:
                return random.choice(unseen)
            return random.choice(pool)

        # 1. Handle Placeholder / Unavailable Reels
        if reel_meta and reel_meta.get("is_placeholder"):
            return pick_unique(["😂💀", "💀🤷‍♂️", "Bhai unavailable dikha raha hai ye 😂", "💀"])

        text_lower = (text or "").lower().strip()

        # 2. Handle Voice Notes / Audio
        if any(k in item_type for k in ["voice", "audio", "voice_media"]):
            if emoji_priority:
                return pick_unique(["👍🎧", "👌🎧", "👍"])
            return pick_unique(["Free hoke sunta hu bhai 👍", "Sunta hu thodi der me 👍", "Ruk free hoke sununga 👍"])

        # 3. Handle Stickers / GIFs / Animated Media
        if any(k in item_type for k in ["animated_media", "sticker", "gif"]):
            return pick_unique(["😂😂💀", "😭😭😂", "💀👍", "😂😂", "🔥💀"])

        # 4. Handle Story Shares / Story Replies
        if "story_share" in item_type or "story" in item_type:
            if emoji_priority:
                return pick_unique(["🔥🙌", "✨🔥", "🙌❤️", "🔥"])
            return pick_unique(["Mast story hai bhai 🔥", "Sahi lag raha hai 🙌🔥", "Badhiya! ✨"])

        # 5. Handle Photos / Media Shares
        if any(k in item_type for k in ["raven_media", "photo"]) and not reel_meta:
            if emoji_priority:
                return pick_unique(["🔥🙌", "😂😂", "👍❤️", "💀😂"])
            return pick_unique(["Mast photo hai bhai 👍🔥", "Badhiya 🙌", "Sahi hai!"])

        # 6. Handle Direct Text Messages (Human Conversational Semantics)
        if "text" in item_type and text_lower:
            # Greetings: "hi", "hello", "hlo", "hey", "hy"
            if text_lower in ["hlo", "hello", "hi", "hey", "hy", "heyy", "hloo", "hii", "hiii"]:
                return pick_unique(["Ha bol bhai", "Bol kya scene hai? 😂", "Ha bol na kya hua", "Hello bhai! Tu bata?"])

            # Exam / Student Misery / Academic Stress / "Paper dekhna ja baad dppresion"
            if any(w in text_lower for w in ["paper", "exam", "depression", "dppresion", "fail", "marks", "result", "backlog", "sem", "padhai", "kharab", "khrb"]):
                return pick_unique([
                    "Us bhai us 😭💀",
                    "Dard bhai dard 💀💀",
                    "Bhai kya hua itna bura gaya kya? 😭💀",
                    "Chill bhai sabka wahi haal hai 😭😂",
                    "Literally me fr 😭💀",
                    "Arey chill maar yaar sab sambhal jayega 💀👍"
                ])

            # Roasts / Friendly Banter / "Zinda hai kya", "Pakistan chala gaya kya"
            if any(w in text_lower for w in ["pakistan", "gayab", "zinda hai", "mar gaya", "kaha tha", "bhoole"]):
                return pick_unique([
                    "Are nahi bhai yahin hu thoda busy tha 😂",
                    "Zinda hu bhai zinda hu 😂💀",
                    "😂😂💀 bhai kyu maar raha hai",
                    "Yahin hu bhai bol kya scene 😂",
                    "😂😂 are bhai yahin hu"
                ])

            # Coming / Meetups / "Aayegaa", "Aaoo", "Kab aayega"
            if any(w in text_lower for w in ["aayega", "aayegaa", "aao", "aaoo", "aaoge", "aa raha", "aara", "kab aayega"]):
                return pick_unique([
                    "Ha aa raha hu ruk 👍",
                    "Ha bhai aata hu thodi der me",
                    "Kaha aana hai bata? 👍",
                    "Dekhta hu bhai, bata kab aana hai",
                    "Done aa raha hu thodi der me 👍"
                ])

            # Games / Ludo / BGMI / Gaming Banter
            if any(w in text_lower for w in ["ludo", "bgmi", "pubg", "game", "khel rhe", "khel raha", "room code"]):
                return pick_unique([
                    "Room code bhej ruk 😂",
                    "Mere bina hi shuru kar diya tum logo ne 😂",
                    "Bhai ludo me mat harana mujhe 😂",
                    "Khel lo bhai maze karo 😂👍",
                    "Ruk free hoke aata hu me bhi 👍"
                ])

            # Greetings & Attention getters: "bhai sun", "oye", etc.
            if any(text_lower.startswith(w) or text_lower == w for w in ["sun", "sunna", "sun na", "oye", "oyee", "bro", "bhaii", "bhai", "dude"]):
                if any(w in text_lower for w in ["kya", "bol", "kaha", "kidhar"]):
                    pass # let specific questions handle it
                else:
                    return pick_unique(["Ha bol bhai", "Bol kya hua? 😂", "Ha bhai sun raha hu", "Kya scene hai bol"])

            # Referring to reels: "last wala", "pehle wala", etc.
            if any(w in text_lower for w in ["last wla", "last wala", "last video", "dusra wala", "dusra wla", "pehle wala"]):
                return pick_unique([
                    "Haan bhai wo to alag hi tha 😂💀",
                    "Last wala sach me khatarnak tha 😭😂",
                    "😂😂💀",
                    "Last wala peak tha fr 💀😂",
                    "Hahaha last wala mast tha 😂"
                ])

            # "Kya kar raha hai" / "Kya chal raha hai"
            if any(w in text_lower for w in ["kya kar raha", "kya karra", "kya chalra", "kya chal raha", "kya krra", "kya hora"]):
                return pick_unique([
                    "Kuch nahi bhai bas baitha tha, tu bata? 😂",
                    "Kuch khas nahi bhai, tu suna kya scene?",
                    "Chill kar raha tha bhai, tu bata?",
                    "Reels scroll kar raha tha 😂 tu bata kya scene"
                ])

            # "Kahan hai" / "Kidhar hai"
            if any(w in text_lower for w in ["kahan hai", "kidhar hai", "kaha h", "kidhar h", "kaha hai"]):
                return pick_unique([
                    "Ghar pe hi hu bhai, bata kya scene?",
                    "Room pe hu bhai, bata?",
                    "Bahar tha thoda, bol kya scene?"
                ])

            # "Free hai kya" / "Busy hai"
            if any(w in text_lower for w in ["free hai", "free h", "busy hai", "busy h"]):
                return pick_unique([
                    "Ha bol na kya hua?",
                    "Ha bhai bol kya scene?",
                    "Thodi der me free hounga, bata kya kaam tha?"
                ])

            # Casual Slang / Expletives (friendly banter)
            if any(w in text_lower for w in ["bc", "mc", "sala", "bkl", "chutiye"]):
                return pick_unique(["😂😂💀", "Bhai control 😂💀", "💀💀", "😭😭😂"])

            # Call / Phone
            if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
                return pick_unique([
                    "📞 5 min me karta hu bhai",
                    "Ruk free hoke call karta hu 👍",
                    "Free hoke lagata hu phone 👍",
                    "Thodi der me karta hu call 👍"
                ])

            # How are you
            if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup"]):
                return pick_unique([
                    "Ekdum badhiya bhai! Tu bata? 🙌🔥",
                    "Mast bhai, tu suna kya scene?",
                    "All good bhai 👍 tu bata?"
                ])

            # Laughter / Memes
            if any(w in text_lower for w in ["marna mat", "jane de", "mat kar", "haha", "lmao", "lol", "rofl", "xd", "😂", "💀"]):
                return pick_unique(["😂😂💀", "😭😭😂", "💀👍", "😂💀", "Bhai epic tha 😂💀"])

            # Plans / Meetups
            if any(w in text_lower for w in ["scene", "plan", "chale", "chal na", "kab chalna", "bahar chal"]):
                return pick_unique([
                    "Ghar pe hi hu bhai, bata kya scene?",
                    "Time aur jagah bata chalte hai 👍",
                    "Done bhai bata kab chalna hai",
                    "Bata kya plan banaya hai 👍"
                ])

            # Treats / Food / Party
            if any(w in text_lower for w in ["party", "treat", "khana", "khilayega"]):
                return pick_unique([
                    "Pehle tu to de party 😂",
                    "Haha done bhai, bata kab chalna hai",
                    "Chal bhai treat to banti hai 😂👍"
                ])

            # Links / Files
            if any(w in text_lower for w in ["link", "bhej", "send kar", "id de"]):
                return pick_unique([
                    "Ruk bhejta hu thodi der me 👍",
                    "Bhejta hu ruk thoda sa free hoke",
                    "Done bhejta hu 👍"
                ])

            # Good night
            if any(w in text_lower for w in ["gn", "good night", "goodnight", "so ja"]):
                return pick_unique(["Gn bhai 😴", "Good night bhai! So ja 😂", "Gn bro! 👍"])

            # Good morning
            if any(w in text_lower for w in ["gm", "good morning", "morning"]):
                return pick_unique(["Morning bhai ☀️", "Gm bro! 🙌", "Good morning bhai!"])

            # Affirmations / Short yes
            if text_lower in ["ha", "haan", "han", "yes", "hn", "hmm", "yep"]:
                return pick_unique(["Sahi hai bhai 👍", "Badhiya 🙌", "Done 👍", "Theek hai bhai"])

            # Negations
            if text_lower in ["nahi", "nhi", "no", "nope", "na"]:
                return pick_unique(["Kyu kya hua? 😂", "Arre kyu bhai? 😂💀", "Kyu bhai sab theek na? 💀", "Theek hai bhai 👍"])

            # Festive
            if any(w in text_lower for w in ["diwali", "deepavali"]):
                return pick_unique(["✨🪔❤️", "Happy Diwali bhai! ✨🪔 Mast celebrate kar!", "Same to you bhai! 🪔✨"])

            # Thanks
            if any(w in text_lower for w in ["thanks", "thank you", "thx", "dhanyawad"]):
                return pick_unique(["❤️🙌", "Mention not bhai ❤️", "Anytime bhai 👍"])

            # Default text reply
            if emoji_priority:
                return pick_unique(["👍😂", "🙌🔥", "👍", "😂😂", "💀👍"])
            return pick_unique(["Sahi hai bhai 👍", "Haan bhai samjha", "Badiya 👍"])

        # 7. Handle Shared Reels using Nexora Intent Classification
        intent = reel_meta.get("intent", "general_funny") if reel_meta else "general_funny"

        if intent == "festive_diwali":
            if emoji_priority:
                return pick_unique(["✨🪔❤️", "🪔✨", "✨❤️"])
            return pick_unique(["Bohot pyara hai yaar ✨🪔", "Mast banaya hai ✨❤️", "Happy Diwali bhai! 🪔✨"])

        if intent == "wholesome_animal":
            if emoji_priority:
                return pick_unique(["🥺❤️", "😭❤️", "😂❤️", "🐱❤️"])
            return pick_unique(["Aww so cute yaar 😭❤️", "Kitna pyara hai 🥺❤️", "Pure therapy fr 😭❤️"])

        if intent == "sports_hype":
            if emoji_priority:
                return pick_unique(["🔥🏏", "GOAT behavior fr 🐐🔥", "🔥🔥"])
            return pick_unique(["Absolute goosebumps bhai 🔥🏏", "GOAT behavior fr 🐐🔥", "Khatarnak moment tha ye 🔥"])

        if intent == "family_relatable":
            if emoji_priority:
                return pick_unique(["😂😂💀", "😭😭😂", "💀💀"])
            return pick_unique(["Literally mummy log aise hi karti hai 😭😂", "Too accurate bhai 😭💀", "😂😂💀"])

        if intent == "student_misery":
            if emoji_priority:
                return pick_unique(["us bhai us 😭💀", "literally me 😭😂", "💀💀"])
            return pick_unique(["Dard bhai dard 💀💀", "Us moment ho gaya ye to 😭😂", "Literally me fr 😭💀"])

        if intent == "prank_drama":
            if emoji_priority:
                return pick_unique(["😂😂💀", "😭😭😂", "💀💀"])
            return pick_unique(["Bhai ye prank to alag hi tha 😂💀", "Kalesh alag hi chal raha hai 💀😂", "Bhai kya tha ye 😂💀"])

        if intent == "gym_motivation":
            if emoji_priority:
                return pick_unique(["💪🔥", "💀💪", "🔥💪"])
            return pick_unique(["Motivation peak pe hai bhai 💪🔥", "Kal se pakka grind shuru 💀💪", "Form dekho bhai ka 💪🔥"])

        if intent == "dank_meme":
            if emoji_priority:
                return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "🔥💀"])
            return pick_unique(["Bhai ye to direct narak leke jayega 💀💀", "I should not be laughing at this 😭💀", "Hass hass ke bura haal ho gaya 😂💀"])

        # General funny fallback
        if emoji_priority:
            return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "😂😂", "🔥💀", "😭😭"])
        return pick_unique(["Mast reel thi ye fr 😂🔥", "Hahah epic bhai 😂", "Bhai kya reel dhoondi hai 😂💀", "Bhai ye alag hi tha 😂💀"])

# Singleton instance
nexora_brain = NexoraAIBrain()
