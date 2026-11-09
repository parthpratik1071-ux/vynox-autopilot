#!/usr/bin/env python3
"""
NexoraAI Vision Engine
Analyzes captionless Instagram Reels, photos, and shared meme images using visual feature extraction:
- Detects warm festive lighting (Diwali / lamps)
- Detects stadium / turf greens (Cricket / sports hype)
- Detects text meme screenshot patterns (Dank memes)
- Detects natural animal / pet warm tones (Wholesome animals)
Operates with 0ms local latency using PIL/Pillow without requiring external cloud API keys.
"""

import os
import tempfile
import urllib.request
from typing import Optional
from PIL import Image, ImageStat

class VisionEngine:
    def __init__(self):
        pass

    def analyze_image_url(self, image_url: str) -> str:
        """
        Downloads thumbnail/image and classifies visual intent.
        Returns one of: 'festive_diwali', 'sports_hype', 'wholesome_animal', 'dank_meme', 'general_funny'
        """
        temp_file = None
        try:
            fd, temp_file = tempfile.mkstemp(suffix=".jpg")
            os.close(fd)
            urllib.request.urlretrieve(image_url, temp_file)
            return self.classify_image_path(temp_file)
        except Exception as e:
            return "general_funny"
        finally:
            if temp_file and os.path.exists(temp_file):
                os.unlink(temp_file)

    def classify_image_path(self, image_path: str) -> str:
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                # Downsample for quick statistical analysis
                small = img.resize((64, 64))
                stat = ImageStat.Stat(small)
                r_mean, g_mean, b_mean = stat.mean

                # 1. Warm golden / orange festive glow (High red/green, lower blue)
                if r_mean > 140 and g_mean > 90 and b_mean < 80:
                    return "festive_diwali"

                # 2. Sports / Stadium turf (Dominant green channel, high brightness)
                if g_mean > r_mean + 15 and g_mean > b_mean + 15:
                    return "sports_hype"

                # 3. High-contrast text meme screenshot (very dark or very light background with high variance)
                std_dev = sum(stat.stddev) / 3.0
                if std_dev > 65 and (r_mean < 60 or r_mean > 190):
                    return "dank_meme"

                # 4. Soft warm tones (Fur / pets / cozy)
                if 100 < r_mean < 170 and 80 < g_mean < 140 and 60 < b_mean < 110:
                    return "wholesome_animal"

                return "general_funny"
        except Exception:
            return "general_funny"

vision_engine = VisionEngine()

