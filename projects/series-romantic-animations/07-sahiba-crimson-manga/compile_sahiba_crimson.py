#!/usr/bin/env python3
"""
Compile 1080x1920 Full HD "Crimson Graphite Manga" Reel for "Sahiba" by Aditya Rikhari.
Visual style inspired by @__.dyrroth:
- Monochrome charcoal/ivory manga line art on solid deep burgundy-crimson canvas
- Combines Blurred Crimson Drop-Shadow PiP Cards, Pitch-Black Anamorphic Cinema Bars,
  Seamless Deep Crimson Macro Panning, and Asymmetric High-Impact Romanized Lyrics.
"""

import subprocess
from pathlib import Path
from PIL import Image
import numpy as np

PROJECT_DIR = Path(
    "/home/pratik/stickman-video-director/projects/series-romantic-animations/07-sahiba-crimson-manga"
)
AUDIO_DIR = PROJECT_DIR / "audio"
ASSETS_DIR = PROJECT_DIR / "assets"
OUT_DIR = PROJECT_DIR / "output"
OUT_DIR.mkdir(parents=True, exist_ok=True)

FFMPEG = "/home/pratik/.local/bin/ffmpeg"
AUDIO_FILE = AUDIO_DIR / "sahiba_clip.wav"
FPS = 30
TOTAL_DUR = 22.50


def sec_to_ass(s: float) -> str:
    h = int(s // 3600)
    m = int((s % 3600) // 60)
    sec = s % 60
    return f"{h:01d}:{m:02d}:{sec:05.2f}"


def sample_border_hex(img_path: Path) -> str:
    """Samples the median burgundy RGB from the image top border for seamless canvas extension."""
    arr = np.array(Image.open(img_path).convert("RGB"))
    strip = arr[:20, :, :].reshape(-1, 3)
    med = np.median(strip, axis=0).astype(int)
    return f"#{med[0]:02x}{med[1]:02x}{med[2]:02x}"


def build_ass_subtitles() -> Path:
    """Writes crisp, large Romanized English ASS subtitles (strictly zero emojis/boxes)."""
    ass_lines = [
        "[Script Info]",
        "Title: Sahiba - Crimson Graphite Manga Reel",
        "ScriptType: v4.00+",
        "WrapStyle: 0",
        "PlayResX: 1080",
        "PlayResY: 1920",
        "",
        "[V4+ Styles]",
        (
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, "
            "OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, "
            "ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
            "Alignment, MarginL, MarginR, MarginV, Encoding"
        ),
        "Style: BrandHeader,DejaVu Sans,30,&H00C8D4FF,&H00000000,&H00080406,&H80000000,-1,0,0,0,100,100,3,0,1,2,2,8,40,40,170,1",
        "Style: CornerLeft,DejaVu Sans,78,&H005858FF,&H00000000,&H00080204,&H80000000,-1,0,0,0,100,100,2,0,1,4.5,4,7,75,75,430,1",
        "Style: CornerRight,DejaVu Sans,68,&H003CE0FF,&H00000000,&H00080204,&H80000000,-1,0,0,0,100,100,2,0,1,4.5,4,3,75,75,450,1",
        "Style: CinemaGold,DejaVu Sans,74,&H002AD4FF,&H00000000,&H00000000,&H00000000,-1,0,0,0,100,100,2,0,1,3,3,8,50,50,590,1",
        "Style: MainLyric,DejaVu Sans,70,&H00FFFFFF,&H000000FF,&H00060204,&H90000000,-1,0,0,0,100,100,2,0,1,4,4,2,60,60,390,1",
        "Style: DropTitle,DejaVu Sans,54,&H003CE0FF,&H00000000,&H00080204,&H80000000,-1,0,0,0,100,100,5,0,1,3,3,2,40,40,390,1",
        "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text",
        # Subtle Persistent Watermark Header
        f"Dialogue: 0,{sec_to_ass(0.3)},{sec_to_ass(22.2)},BrandHeader,,0,0,0,,{{\\fade(300,300)}}SAHIBA  •  @vynox_00000",
        # Beat 1 (Scene 1: Bindi Gaze Card) 0.0 - 6.8s
        f"Dialogue: 1,{sec_to_ass(0.1)},{sec_to_ass(2.4)},CornerLeft,,0,0,0,,{{\\fade(150,200)}}Saahiba...",
        f"Dialogue: 1,{sec_to_ass(2.4)},{sec_to_ass(4.6)},CornerRight,,0,0,0,,{{\\fade(150,200)}}{{\\c&H00FFFFFF&}}aaye ghar {{\\c&H003CE0FF&}}kaahe na...",
        f"Dialogue: 1,{sec_to_ass(4.6)},{sec_to_ass(6.8)},MainLyric,,0,0,0,,{{\\fade(150,150)}}aise toh {{\\c&H005858FF&}}sataaye na...",
        # Beat 2 (Scene 2: Pitch-Black Anamorphic Cinema Cut) 6.8 - 10.5s
        f"Dialogue: 2,{sec_to_ass(6.8)},{sec_to_ass(10.5)},CinemaGold,,0,0,0,,{{\\fade(120,180)}}Dekhoon tujhko...\\N{{\\c&H00FFFFFF&}}chain aata hai",
        # Beat 3 (Scene 3: Payal Full Crimson) 10.5 - 16.5s
        f"Dialogue: 1,{sec_to_ass(10.5)},{sec_to_ass(12.5)},CornerLeft,,0,0,0,,{{\\fade(120,180)}}Saahiba...",
        f"Dialogue: 1,{sec_to_ass(12.5)},{sec_to_ass(14.5)},CornerRight,,0,0,0,,{{\\fade(120,180)}}neend aaye na...",
        f"Dialogue: 1,{sec_to_ass(14.5)},{sec_to_ass(16.5)},MainLyric,,0,0,0,,{{\\fade(120,150)}}raatein kaati {{\\c&H003CE0FF&}}jaaye na...",
        # Beat 4 (Scene 4: Gajra Embrace + 20.0s Beat Drop Climax) 16.5 - 22.5s
        f"Dialogue: 1,{sec_to_ass(16.5)},{sec_to_ass(20.0)},MainLyric,,0,0,0,,{{\\fade(150,150)}}tera hi khayal {{\\c&H003CE0FF&}}din-rain aata hai...",
        f"Dialogue: 2,{sec_to_ass(20.0)},{sec_to_ass(22.4)},DropTitle,,0,0,0,,{{\\fade(100,450)}}SAHIBA  •  ADITYA RIKHARI",
    ]
    ass_path = OUT_DIR / "sahiba_subtitles.ass"
    ass_path.write_text("\n".join(ass_lines), encoding="utf-8")
    return ass_path


def run_shot_ffmpeg(img: Path, out_mp4: Path, dur: float, filter_complex: str) -> None:
    """Runs FFmpeg at locked FPS to generate a single uniform-timebase shot clip."""
    subprocess.run(
        [
            FFMPEG, "-y",
            "-framerate", str(FPS), "-loop", "1", "-i", str(img),
            "-filter_complex", filter_complex,
            "-map", "[outv]",
            "-t", f"{dur:.3f}",
            "-r", str(FPS),
            "-c:v", "libx264", "-preset", "fast", "-crf", "17",
            str(out_mp4),
        ],
        check=True,
    )


def render_pip_shadow_shot(img: Path, out_mp4: Path, dur: float, z_step: float = 0.0007) -> None:
    """Renders blurred crimson macro background + sharp floating card with drop shadow."""
    frames = int(round(dur * FPS))
    filter_complex = (
        f"[0:v]fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=30:6,eq=brightness=-0.18:contrast=1.16[bg];"
        f"color=c=#040102@0.88:s=940x528:r={FPS}[shadow];"
        f"[0:v]scale=2752:1536,"
        f"zoompan=z='min(zoom+{z_step},1.14)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':"
        f"d={frames}:s=940x524:fps={FPS}[fg];"
        f"[bg][shadow]overlay=x=88:y=696:shortest=1[bgs];"
        f"[bgs][fg]overlay=x=70:y=678:shortest=1,format=yuv420p[outv]"
    )
    run_shot_ffmpeg(img, out_mp4, dur, filter_complex)


def render_anamorphic_cinema_shot(img: Path, out_mp4: Path, dur: float) -> None:
    """Renders pitch-black anamorphic letterbox cut focusing across the blushing close-up."""
    frames = int(round(dur * FPS))
    filter_complex = (
        f"color=c=#040203:s=1080x1920:r={FPS}[black];"
        f"[0:v]crop=1376:520:0:95,scale=2160:816,"
        f"zoompan=z='min(1.03+0.0008*on,1.12)':x='iw*0.54-(iw/zoom/2)':y='ih*0.50-(ih/zoom/2)':"
        f"d={frames}:s=1080x440:fps={FPS}[strip];"
        f"[black][strip]overlay=x=0:y=750:shortest=1,format=yuv420p[outv]"
    )
    run_shot_ffmpeg(img, out_mp4, dur, filter_complex)


def render_seamless_crimson_shot(img: Path, out_mp4: Path, dur: float) -> None:
    """Renders seamless deep burgundy studio canvas with feathered edge blend on Payal macro."""
    frames = int(round(dur * FPS))
    bg_hex = sample_border_hex(img)
    filter_complex = (
        f"color=c={bg_hex}:s=1080x1920:r={FPS}[canvas];"
        f"[0:v]scale=2752:1536,"
        f"zoompan=z='min(1.0+0.0006*on,1.11)':x='iw/2-(iw/zoom/2)':y='ih*0.52-(ih/zoom/2)':"
        f"d={frames}:s=1080x604:fps={FPS},"
        f"format=yuva420p,"
        f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)':"
        f"a='if(lt(Y,36),255*(Y/36),if(gt(Y,H-36),255*((H-Y)/36),255))'[fg];"
        f"[canvas][fg]overlay=x=0:y=658:shortest=1,vignette=PI/5,format=yuv420p[outv]"
    )
    run_shot_ffmpeg(img, out_mp4, dur, filter_complex)


def render_climax_beatdrop_shot(img: Path, out_mp4: Path, dur: float) -> None:
    """Renders emotional embrace card transitioning with a rose-white beat-drop pulse at 3.5s."""
    frames = int(round(dur * FPS))
    filter_complex = (
        f"[0:v]fps={FPS},scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"boxblur=28:6,eq=brightness=-0.16:contrast=1.18[bg];"
        f"color=c=#040102@0.88:s=1000x562:r={FPS}[shadow];"
        f"[0:v]scale=2752:1536,"
        f"zoompan=z='min(1.02+0.0007*on,1.15)':x='iw*0.48-(iw/zoom/2)':y='ih*0.47-(ih/zoom/2)':"
        f"d={frames}:s=1000x558:fps={FPS}[fg];"
        f"[bg][shadow]overlay=x=56:y=678:shortest=1[bgs];"
        f"[bgs][fg]overlay=x=40:y=660:shortest=1,"
        f"eq=brightness='if(between(t,3.45,3.70),0.28*(1-(t-3.45)/0.25),0)':"
        f"saturation='if(gt(t,3.50),1.15,1.0)',"
        f"format=yuv420p[outv]"
    )
    run_shot_ffmpeg(img, out_mp4, dur, filter_complex)


def main() -> None:
    ass_path = build_ass_subtitles()
    print(f"📝 ASS subtitles generated: {ass_path}")

    s1 = OUT_DIR / "shot_0.mp4"
    s2 = OUT_DIR / "shot_1.mp4"
    s3 = OUT_DIR / "shot_2.mp4"
    s4 = OUT_DIR / "shot_3.mp4"

    print("🎬 Rendering Shot 1/4: Blurred Crimson PiP Card (Bindi Gaze, 6.8s)...")
    render_pip_shadow_shot(ASSETS_DIR / "scene-1.jpg", s1, 6.8)

    print("🎬 Rendering Shot 2/4: Anamorphic Pitch-Black Cinema Cut (Blushing Touch, 3.7s)...")
    render_anamorphic_cinema_shot(ASSETS_DIR / "scene-2.jpg", s2, 3.7)

    print("🎬 Rendering Shot 3/4: Seamless Crimson Studio Macro (Payal Ankles, 6.0s)...")
    render_seamless_crimson_shot(ASSETS_DIR / "scene-3.jpg", s3, 6.0)

    print("🎬 Rendering Shot 4/4: Climax Embrace & Beat Drop Pulse (Gajra Embrace, 6.0s)...")
    render_climax_beatdrop_shot(ASSETS_DIR / "scene-4.jpg", s4, 6.0)

    concat_list = OUT_DIR / "shots_concat.txt"
    concat_list.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in (s1, s2, s3, s4)) + "\n",
        encoding="utf-8",
    )

    raw_visual = OUT_DIR / "raw_visual.mp4"
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list), "-c", "copy", str(raw_visual)],
        check=True,
    )

    final_mp4 = OUT_DIR / "film_sahiba_crimson_manga.mp4"
    print("🔥 Burning Crimson Typography & Muxing Audio Track...")
    subprocess.run(
        [
            FFMPEG, "-y",
            "-i", str(raw_visual),
            "-i", str(AUDIO_FILE),
            "-vf", f"ass={ass_path.resolve()}",
            "-af", "volume=6dB,alimiter=limit=0.93:attack=5:release=60",
            "-r", str(FPS),
            "-c:v", "libx264", "-preset", "slow", "-crf", "17",
            "-c:a", "aac", "-b:a", "256k",
            "-movflags", "+faststart",
            "-shortest",
            str(final_mp4),
        ],
        check=True,
    )

    cover_jpg = OUT_DIR / "cover.jpg"
    subprocess.run(
        [FFMPEG, "-y", "-ss", "00:00:01.200", "-i", str(final_mp4), "-frames:v", "1", "-q:v", "2", "-update", "1", str(cover_jpg)],
        check=True,
    )

    # Save verification previews for shots 2, 3, and 4
    for fname, ts in [
        ("check_cinema_frame.jpg", "00:00:08.500"),
        ("check_payal.jpg", "00:00:13.500"),
        ("check_climax.jpg", "00:00:18.500"),
    ]:
        subprocess.run(
            [FFMPEG, "-y", "-ss", ts, "-i", str(final_mp4), "-frames:v", "1", "-q:v", "2", "-update", "1", str(OUT_DIR / fname)],
            check=True,
        )

    for tmp in (s1, s2, s3, s4, raw_visual, concat_list):
        if tmp.exists():
            tmp.unlink()

    print(f"\n🎉 Successfully compiled Crimson Graphite Manga Reel: {final_mp4}")
    print(f"🖼️ Cover Thumbnail: {cover_jpg}")


if __name__ == "__main__":
    main()
