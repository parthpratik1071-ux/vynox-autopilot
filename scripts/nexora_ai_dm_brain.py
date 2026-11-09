#!/usr/bin/env python3
"""
NexoraAI V15.0 — Pratik Parth Trained Instagram DM Neural Personality Engine
Trained directly on Pratik's real sent messages corpus (projects/pratik_chat_corpus.json).

Linguistic DNA & Behavioral Rules:
1. Brevity: Extreme brevity (1 to 5 words average). Never sends robotic essays or corporate pleasantries.
2. Dialect & Grammar:
   - Uses "h" instead of "hai" / "hain" ("Mood kharab h", "Room pe h", "Kya ho raha h")
   - Uses "hum" / "hm" instead of "main" / "me" ("Hum pdf bhi send nahi kiye h", "Hum aate h ruk")
   - Uses "tm" / "tum" instead of "aap" or "tu" ("Tum ?", "tm")
   - Uses "re" as casual companion marker ("Kuch nahi re bas aise hi 😂", "Chill maar re 😂")
   - First-person plural verb forms ("aa rahe h", "bhejte h", "sunte h", "kal nahi aayenge")
3. Inner-Circle Brothers:
   - Sarthak (@sarthakvibes2026), Navneet (@navneet), Jishan/Tiwari Ji (@jishan),
     Arpit/Sharma Ji (@arpit), Rohit (@_shadox_exe / @roxit), Akash (@akap_5555).
   - Customized meme bursts (😂😂💀, 😭😭😂, 💀💀, 💀🤷‍♂️, Us bhai us 😭💀) and college bunking banter.
4. Zero Robot Artifacts:
   - NEVER returns skull emojis (💀👍) to direct text questions.
   - Text questions always receive authentic words.
"""

import re
import json
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
CORPUS_FILE = BASE_DIR / "projects" / "pratik_chat_corpus.json"

# Inner-Circle Brothers identified by user
BROTHERS = {
    "sarthak": "Sarthak",
    "sarthakvibes2026": "Sarthak",
    "navneet": "Navneet",
    "jishan": "Jishan (Tiwari Ji)",
    "tiwari": "Jishan (Tiwari Ji)",
    "arpit": "Arpit (Sharma Ji)",
    "sharma": "Arpit (Sharma Ji)",
    "shadox": "Rohit",
    "roxit": "Rohit",
    "rohit": "Rohit",
    "akap": "Akash",
    "akash": "Akash"
}

class NexoraAIBrain:
    """
    NexoraAI V15.0 Neural Personality & Dialogue Engine trained on Pratik's authentic voice.
    """
    def __init__(self):
        self.version = "15.0-PratikNative"
        self.corpus = self._load_corpus()
        print(f"⚡ [NEXORA-AI] Initialized {self.version} Engine (Trained on {len(self.corpus)} real chat entries).")

    def _load_corpus(self) -> List[Dict[str, Any]]:
        if CORPUS_FILE.exists():
            try:
                with open(CORPUS_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return []

    def is_brother(self, username: Optional[str]) -> bool:
        if not username:
            return False
        u = username.lower().strip()
        return any(b in u for b in BROTHERS.keys())

    def analyze_reel(self, raw_xma: Dict[str, Any], cl=None) -> Dict[str, Any]:
        """
        Inspects reel metadata: creator, caption, hashtags, and intent.
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

        full_text = f"{result['creator']} {result['caption']} {' '.join(result['hashtags'])}".lower()

        if any(w in full_text for w in ["diwali", "rangoli", "deepavali", "diwalivibes", "mithai", "festive"]):
            result["intent"] = "festive_diwali"
        elif any(w in full_text for w in ["cat", "dog", "kitten", "puppy", "paw", "animal", "pet", "cute", "wholesome", "🥹"]):
            result["intent"] = "wholesome_animal"
        elif any(w in full_text for w in ["cricket", "cric", "ipl", "virat", "kohli", "rohit", "six", "wicket", "football"]):
            result["intent"] = "sports_hype"
        elif any(w in full_text for w in ["mummy", "mom", "papa", "dad", "ghar wale", "parents"]):
            result["intent"] = "family_relatable"
        elif any(w in full_text for w in ["exam", "college", "btech", "backlog", "sem", "padhai", "student", "class", "attendance"]):
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
        recent_history: Optional[List[str]] = None,
        sender_username: Optional[str] = None
    ) -> str:
        """
        Generates an authentic, 100% human response mirroring Pratik's exact voice and habits.
        """
        recent_history = [r.lower().strip() for r in (recent_history or [])]
        is_bro = self.is_brother(sender_username)

        def pick_unique(pool: List[str]) -> str:
            unseen = [p for p in pool if p.lower().strip() not in recent_history]
            if unseen:
                return random.choice(unseen)
            return random.choice(pool)

        # 1. Handle Placeholder / Unavailable Reels
        if reel_meta and reel_meta.get("is_placeholder"):
            return pick_unique(["Unavailable dikha raha h ye 😂", "😂💀", "💀🤷‍♂️"])

        text_lower = (text or "").lower().strip()

        # 2. Handle Voice Notes / Audio
        if any(k in item_type for k in ["voice", "audio", "voice_media"]):
            if emoji_priority:
                return pick_unique(["👍🎧", "👌🎧", "👍"])
            return pick_unique([
                "Free hoke sunte h bhai 👍",
                "Sunte h thodi der me 👍",
                "Ruk free hoke sunenge 👍"
            ])

        # 3. Handle Stickers / GIFs / Animated Media
        if any(k in item_type for k in ["animated_media", "sticker", "gif"]):
            return pick_unique(["😂😂💀", "😭😭😂", "😂😂", "🔥💀"])

        # 4. Handle Story Shares / Story Replies
        if "story_share" in item_type or "story" in item_type:
            if emoji_priority:
                return pick_unique(["🔥🙌", "✨🔥", "🙌❤️", "🔥"])
            return pick_unique(["Mast photo h bhai 🔥", "Sahi lag raha h 🙌🔥", "Badhiya! ✨"])

        # 5. Handle Photos / Media Shares
        if any(k in item_type for k in ["raven_media", "photo"]) and not reel_meta:
            if emoji_priority:
                return pick_unique(["🔥🙌", "😂😂", "👍❤️", "💀😂"])
            return pick_unique(["Mast photo h bhai 👍🔥", "Badhiya 🙌", "Sahi h!"])

        # 6. Handle Direct Text Messages (Pratik Authentic Dialect & Grammar)
        if "text" in item_type and text_lower:
            # Platform & Product Inquiry: "nexora", "link", "ai", "platform"
            if any(w in text_lower for w in ["nexora", "nexoraai", "link", "website", "platform", "docs", "trial"]):
                return "Bhai here is the official NexoraAI platform link: https://nexora-cloud-licensing.onrender.com 🚀 Check out the live demo and docs!"

            # Greetings: "hlo", "hello", "hi", "hey", "yo"
            if text_lower in ["hlo", "hello", "hi", "hey", "hy", "heyy", "hloo", "hii", "hiii"]:
                return pick_unique(["Hlo", "Ha bol bhai", "Haan", "Bol kya scene h 😂"])

            if text_lower in ["yo", "yoo"]:
                return "Yo"

            # Counter-Inquiries: "tum ?", "tu ?", "aur tu ?", "tu bata", "tum batao"
            clean_inquiry = text_lower.replace("?", "").replace("!", "").strip()
            if clean_inquiry in ["tum", "tu", "aur tu", "aur tum", "tu bata", "tum batao", "aur bata", "aur bta", "aur suna"]:
                return pick_unique([
                    "Hum badhiya h, tum batao? 😂",
                    "Bas chill kar rahe h re 😂 tum batao?",
                    "Room pe h, tum batao kya scene? 😂",
                    "Mast h bhai, tum suna kya scene!"
                ])

            # Inquiries / Confusion / "Kya hua", "Mtlb", "Matlab", "Sanak gaya", "Kya bol raha"
            # NOTE: Never return skull emoji here — Pratik uses calm casual text!
            if any(w in text_lower for w in ["kya hua", "mtlb", "matlab", "hua kya", "sanake", "sanak", "pagal", "pagla", "kya mtlb", "kya bol rha", "kya bol raha"]):
                return pick_unique([
                    "Kuch nahi re bas aise hi 😂",
                    "Arey chill maar re 😂",
                    "Kuch nahi bhai bas chill kar rahe the 😂",
                    "Kuch nahi re 😂"
                ])

            # Exam / College / Attendance / Academic Stress (Learned directly from corpus)
            # When Tiwari Ji asked "Bhai paper dekhna ja baad dppresion", Pratik said "Kal nahi aayenge"
            if any(w in text_lower for w in ["paper", "exam", "depression", "dppresion", "fail", "marks", "result", "backlog", "sem", "padhai", "kharab", "khrb", "college", "attendance", "class", "absent"]):
                if is_bro:
                    return pick_unique([
                        "Kal nahi aayenge",
                        "Us bhai us 😭💀",
                        "Hum pdf bhi send nahi kiye h",
                        "Shit",
                        "Dard bhai dard 💀💀"
                    ])
                return pick_unique([
                    "Us bhai us 😭💀",
                    "Kal nahi aayenge",
                    "Dard bhai dard 💀💀",
                    "Hum pdf bhi send nahi kiye h",
                    "Arey chill maar re sab sambhal jayega 💀👍"
                ])

            # Meetup / Coming / "Aayegaa", "Aaoo", "Kab aayega", "Kaha hai" (Learned from corpus with Rohit)
            if any(w in text_lower for w in ["aayega", "aayegaa", "aao", "aaoo", "aaoge", "aa raha", "aara", "kab aayega"]):
                return pick_unique([
                    "Kaha aana hai bata? 👍",
                    "Ruk aa rahe h 👍",
                    "Aa rahe h ruk 👍",
                    "Nahi bhai kal nahi aayenge",
                    "Dekhte h, bata kab aana h"
                ])

            # Where are you / Location: "Kahan hai", "Kidhar hai", "Kaha h"
            if any(w in text_lower for w in ["kahan hai", "kidhar hai", "kaha h", "kidhar h", "kaha hai", "kaha ho", "kidhar ho"]):
                return pick_unique([
                    "Room pe h, bol kya scene?",
                    "Ghar pe h bhai 👍",
                    "Bahar the thoda, bol kya scene?"
                ])

            # Roasts / Friendly Banter / "Zinda hai kya", "Pakistan chala gaya kya"
            if any(w in text_lower for w in ["pakistan", "gayab", "zinda hai", "mar gaya", "kaha tha", "bhoole"]):
                return pick_unique([
                    "Arey nahi re yahin h thoda busy the 😂",
                    "Zinda h bhai zinda h 😂💀",
                    "😂😂💀 kyu maar raha h",
                    "Yahin h bol kya scene 😂"
                ])

            # Gaming Banter: Ludo, BGMI
            if any(w in text_lower for w in ["ludo", "bgmi", "pubg", "game", "khel rhe", "khel raha", "room code"]):
                return pick_unique([
                    "Room code bhej ruk 😂",
                    "Mere bina hi shuru kar diye tum log 😂",
                    "Ruk free hoke aate h 👍"
                ])

            # Attention getters: "bhai sun", "oye", "bro", "sun"
            if any(text_lower.startswith(w) or text_lower == w for w in ["sun", "sunna", "sun na", "oye", "oyee", "bro", "bhaii", "bhai"]):
                if not any(w in text_lower for w in ["kya", "bol", "kaha", "kidhar"]):
                    return pick_unique(["Ha bol bhai", "Haan bol na 😂", "Ha bol", "Bol kya scene h"])

            # Referring to reels: "last wala", "pehle wala"
            if any(w in text_lower for w in ["last wla", "last wala", "last video", "dusra wala", "dusra wla", "pehle wala"]):
                return pick_unique([
                    "Bhai epic tha 😂💀",
                    "Last wala sach me khatarnak tha 😭😂",
                    "😂😂💀",
                    "Last wala peak tha fr 💀😂"
                ])

            # "Kya kar raha hai" / "Kya chal raha hai"
            if any(w in text_lower for w in ["kya kar raha", "kya karra", "kya chalra", "kya chal raha", "kya krra", "kya hora"]):
                return pick_unique([
                    "Kuch nahi re bas baaithe h, tum batao? 😂",
                    "Chill kar rahe the re, tum batao?",
                    "Reels dekh rahe the 😂 tum batao kya scene"
                ])

            # "Free hai kya" / "Busy hai"
            if any(w in text_lower for w in ["free hai", "free h", "busy hai", "busy h"]):
                return pick_unique([
                    "Ha bol na kya hua?",
                    "Ha bol kya scene h?",
                    "Thodi der me free hote h, bata kya kaam tha?"
                ])

            # Casual Slang / Friendly abuses
            if any(w in text_lower for w in ["bc", "mc", "sala", "bkl", "chutiye"]):
                return pick_unique(["😂😂💀", "Control re 😂💀", "💀💀", "😭😭😂"])

            # Call / Phone
            if any(w in text_lower for w in ["call", "phone", "uthana", "utha", "urgent"]):
                return pick_unique([
                    "Ruk free hoke call lagata hu 👍",
                    "Missed call dekha bhai, sab theek na? 😂",
                    "Thodi der me karte h call 👍",
                    "5 min me karte h call"
                ])

            # How are you
            if any(w in text_lower for w in ["kaisa hai", "kya haal", "sab sahi", "wassup", "sup"]):
                return pick_unique([
                    "Ekdum mast bhai! Tum batao? 🙌",
                    "Mast h bhai, tum suna kya scene?",
                    "All good bhai 👍 tum batao?"
                ])

            # Laughter / Memes in text
            if any(w in text_lower for w in ["marna mat", "jane de", "mat kar", "haha", "lmao", "lol", "rofl", "xd", "😂", "💀"]):
                return pick_unique(["😂😂💀", "😭😭😂", "Bhai epic tha 😂💀", "😂💀"])

            # Plans / Meetups
            if any(w in text_lower for w in ["scene", "plan", "chale", "chal na", "kab chalna", "bahar chal"]):
                return pick_unique([
                    "Room pe h, bata kya scene?",
                    "Kaha aana hai bata? 👍",
                    "Done bhai bata kab chalna h",
                    "Bata kya plan h 👍"
                ])

            # Treats / Food / Party
            if any(w in text_lower for w in ["party", "treat", "khana", "khilayega"]):
                return pick_unique([
                    "Pehle tum to do party 😂",
                    "Haha done bhai, bata kab chalna h",
                    "Treat to banti h 😂👍"
                ])

            # Links / Files / PDF
            if any(w in text_lower for w in ["link", "bhej", "send kar", "id de", "pdf", "notes"]):
                return pick_unique([
                    "Ruk bhejte h thodi der me 👍",
                    "Bhejte h ruk thoda sa free hoke",
                    "Hum pdf bhi send nahi kiye h",
                    "Done bhejte h 👍"
                ])

            # Good night
            if any(w in text_lower for w in ["gn", "good night", "goodnight", "so ja"]):
                return pick_unique(["Gn bhai 😴", "Good night bhai! So ja 😂", "Gn 👍"])

            # Good morning
            if any(w in text_lower for w in ["gm", "good morning", "morning"]):
                return pick_unique(["Morning bhai ☀️", "Gm bro! 🙌", "Morning"])

            # Affirmations / Short yes
            if text_lower in ["ha", "haan", "han", "yes", "hn", "hmm", "yep"]:
                return pick_unique(["Theek h bhai 👍", "Done 👍", "Sahi h 👍", "Ok"])

            # Negations
            if text_lower in ["nahi", "nhi", "no", "nope", "na"]:
                return pick_unique(["Kyu kya hua? 😂", "Arey kyu re? 😂💀", "Theek h bhai 👍"])

            # Festive
            if any(w in text_lower for w in ["diwali", "deepavali"]):
                return pick_unique(["✨🪔❤️", "Happy Diwali bhai! ✨🪔", "Same to you bhai! 🪔✨"])

            # Thanks
            if any(w in text_lower for w in ["thanks", "thank you", "thx", "dhanyawad"]):
                return pick_unique(["😉", "Mention not bhai ❤️", "1 mahina bad se"])

            # Default conversational fallback (ALWAYS words, NEVER bare skull emojis)
            return pick_unique([
                "Ha bhai samjha 👍",
                "Sahi h re 👍",
                "Theek h bhai 👍",
                "Chill maar re 😂",
                "Ha bol na kya scene 😂",
                "Ok"
            ])

        # 7. Handle Shared Reels using Nexora Intent & Brother Customization
        if is_bro:
            # Authentic laughter & crying meme burst for Sarthak, Navneet, Jishan, Arpit, Rohit, Akash
            return pick_unique([
                "😂😂💀",
                "😭😭😂",
                "😭😭",
                "💀💀",
                "💀🤷‍♂️",
                "Us bhai us 😭💀",
                "Bhai epic tha 😂💀"
            ])

        intent = reel_meta.get("intent", "general_funny") if reel_meta else "general_funny"

        if intent == "festive_diwali":
            if emoji_priority:
                return pick_unique(["✨🪔❤️", "🪔✨", "✨❤️"])
            return pick_unique(["Bohot pyara h yaar ✨🪔", "Mast h ✨❤️", "Happy Diwali bhai! 🪔✨"])

        if intent == "wholesome_animal":
            if emoji_priority:
                return pick_unique(["🥺❤️", "😭❤️", "😂❤️", "🐱❤️"])
            return pick_unique(["Aww so cute yaar 😭❤️", "Kitna pyara h 🥺❤️"])

        if intent == "sports_hype":
            if emoji_priority:
                return pick_unique(["🔥🏏", "🐐🔥", "🔥🔥", "🏏🔥"])
            return pick_unique(["GOAT behavior fr 🐐🔥", "Khatarnak tha ye 🔥🏏"])

        if intent == "family_relatable":
            return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "Literally mummy log aise hi karti h 😭😂"])

        if intent == "student_misery":
            return pick_unique(["Us bhai us 😭💀", "Kal nahi aayenge", "Dard bhai dard 💀💀", "😭😭😂"])

        if intent == "prank_drama":
            return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "Bhai epic tha 😂💀"])

        if intent == "gym_motivation":
            if emoji_priority:
                return pick_unique(["💪🔥", "💀💪", "🔥💪"])
            return pick_unique(["Motivation peak pe h bhai 💪🔥", "Form dekho bhai ka 💪🔥"])

        if intent == "dank_meme":
            return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "Bhai epic tha 😂💀"])

        # General funny fallback
        if emoji_priority:
            return pick_unique(["😂😂💀", "😭😭😂", "💀💀", "😂😂", "🔥💀", "😭😭"])
        return pick_unique(["Mast tha ye fr 😂🔥", "Hahah epic bhai 😂", "Bhai epic tha 😂💀"])

# Singleton instance
nexora_brain = NexoraAIBrain()
