#!/usr/bin/env python3
"""Unit tests for Vynox Autopilot posting, booster, duplicate guard, and Graph API adapters."""

import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from PIL import Image

ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = ROOT_DIR / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import daily_dispatcher  # noqa: E402
import daily_trend_producer  # noqa: E402
import duplicate_guard  # noqa: E402
import insta_local_post  # noqa: E402
import reels_booster  # noqa: E402


class TestInstaLocalPost(unittest.TestCase):
    def test_is_restriction_error_detects_markers(self):
        self.assertTrue(insta_local_post.is_restriction_error(RuntimeError("ChallengeRequired: checkpoint")))
        self.assertTrue(insta_local_post.is_restriction_error(RuntimeError("Please wait a few minutes before you try again later")))
        self.assertFalse(insta_local_post.is_restriction_error(RuntimeError("Connection timed out")))

    def test_non_interactive_expired_session_fails_without_hanging(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = Path(tmp) / "insta_session.json"
            sess.write_text("{}")

            fake_client = mock.MagicMock()
            fake_client.get_timeline_feed.side_effect = insta_local_post.LoginRequired("expired")

            with mock.patch.object(insta_local_post, "Client", return_value=fake_client), mock.patch.dict(
                os.environ, {}, clear=True
            ):
                with self.assertRaises(RuntimeError) as ctx:
                    insta_local_post.get_client(session_file=sess, interactive=False)
                self.assertIn("INSTA_GRAPH_ACCESS_TOKEN", str(ctx.exception))

    def test_official_graph_client_fetches_insights_plays(self):
        client = insta_local_post.OfficialGraphClient("tok123", "999")

        def fake_request(path, params=None, method="GET"):
            if path == "999/media":
                return {
                    "data": [
                        {
                            "id": "111",
                            "caption": "Sahiba reel",
                            "permalink": "https://www.instagram.com/reel/AbCdEf12/",
                            "timestamp": "2026-11-12T06:00:00+00:00",
                            "like_count": 42,
                            "comments_count": 7,
                        }
                    ]
                }
            if path == "111/insights":
                if (params or {}).get("metric") == "plays":
                    raise RuntimeError("Graph API 400: invalid metric plays")
                return {"data": [{"values": [{"value": 1250}]}]}
            raise AssertionError(f"Unexpected Graph API path: {path}")

        with mock.patch.object(client, "_request", side_effect=fake_request):
            medias = client.user_medias("999", amount=1)

        self.assertEqual(len(medias), 1)
        self.assertEqual(medias[0].code, "AbCdEf12")
        self.assertEqual(medias[0].play_count, 1250)
        self.assertEqual(medias[0].like_count, 42)
        self.assertEqual(medias[0].comment_count, 7)

    def test_check_auth_health_detects_expired_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = Path(tmp) / "insta_session.json"
            sess.write_text("{}")
            fake_client = mock.MagicMock()
            fake_client.get_timeline_feed.side_effect = insta_local_post.LoginRequired("expired")

            with mock.patch.object(insta_local_post, "Client", return_value=fake_client), mock.patch.dict(
                os.environ, {}, clear=True
            ):
                ok, code, detail = insta_local_post.check_auth_health(session_file=sess)
            self.assertFalse(ok)
            self.assertEqual(code, "SESSION_EXPIRED")
            self.assertIn("LoginRequired", str(detail))

    def test_check_auth_health_detects_valid_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = Path(tmp) / "insta_session.json"
            sess.write_text("{}")
            fake_client = mock.MagicMock()
            fake_client.get_timeline_feed.return_value = {"feed_items": []}

            with mock.patch.object(insta_local_post, "Client", return_value=fake_client), mock.patch.dict(
                os.environ, {}, clear=True
            ):
                ok, code, client = insta_local_post.check_auth_health(session_file=sess)
            self.assertTrue(ok)
            self.assertEqual(code, "SESSION_VALID")
            self.assertEqual(client, fake_client)

    def test_check_auth_health_detects_graph_api(self):
        with mock.patch.dict(
            os.environ,
            {"INSTA_GRAPH_ACCESS_TOKEN": "token_xyz", "INSTA_IG_USER_ID": "17841400002"},
            clear=False,
        ):
            with mock.patch.object(
                insta_local_post.OfficialGraphClient, "account_info", return_value=SimpleNamespace(username="vynox")
            ):
                ok, code, client = insta_local_post.check_auth_health()
            self.assertTrue(ok)
            self.assertEqual(code, "OFFICIAL_GRAPH_API_VALID")
            self.assertIsInstance(client, insta_local_post.OfficialGraphClient)

    def test_export_session_base64_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            sess = Path(tmp) / "insta_session.json"
            sess.write_text(json.dumps({"test_key": "test_val"}))
            b64_str = insta_local_post.export_session_base64(session_file=sess)
            import base64
            decoded = json.loads(base64.b64decode(b64_str.encode()).decode())
            self.assertEqual(decoded.get("test_key"), "test_val")

    def test_official_graph_client_selected_by_env(self):
        with mock.patch.dict(
            os.environ,
            {"INSTA_GRAPH_ACCESS_TOKEN": "token_abc", "INSTA_IG_USER_ID": "17841400001"},
            clear=False,
        ):
            cl = insta_local_post.get_client(interactive=False)
        self.assertIsInstance(cl, insta_local_post.OfficialGraphClient)
        self.assertTrue(getattr(cl, "is_official_graph", False))

    def test_upload_reel_attaches_official_music_metadata(self):
        cl = mock.MagicMock()
        cl.is_official_graph = False
        fake_track = mock.MagicMock()
        fake_track.title = "Kyun Main Jaagoon"
        fake_track.display_artist = "Shafqat Amanat Ali"
        cl.search_music.return_value = [fake_track]
        cl.clip_music_extra_data.return_value = {
            "clips_audio_metadata": {
                "original": {"volume_level": 1.0},
                "song": {"artist_name": "Shafqat Amanat Ali", "audio_asset_id": 12345}
            }
        }
        fake_media = mock.MagicMock(code="XYZ123", pk="987654")
        cl.clip_upload.return_value = fake_media

        with tempfile.TemporaryDirectory() as tmp:
            vid = Path(tmp) / "reel.mp4"
            vid.write_bytes(b"dummy_video_bytes")
            
            res = insta_local_post.upload_reel(
                cl,
                video_path=vid,
                caption="Test caption",
                music_query="Kyun Main Jaagoon (Slowed + Reverb)"
            )
            
            self.assertEqual(res.code, "XYZ123")
            cl.search_music.assert_called_once_with("Kyun Main Jaagoon")
            cl.clip_music_extra_data.assert_called_once_with(
                track=fake_track,
                original_volume=1.0,
                music_volume=0.0
            )
            cl.clip_upload.assert_called_once()
            _, kwargs = cl.clip_upload.call_args
            self.assertIn("extra_data", kwargs)
            self.assertIn("clips_audio_metadata", kwargs["extra_data"])



class TestReelsBooster(unittest.TestCase):
    def _make_booster(self, tmp: Path) -> reels_booster.ReelsBooster:
        return reels_booster.ReelsBooster(
            boosted_file=tmp / "reels_boosted.json",
            cooldown_file=tmp / "booster_cooldown.json",
            analytics_file=tmp / "reel_analytics.json",
            requests_file=tmp / "fan_requests.json",
            leaderboard_file=tmp / "hook_leaderboard.json",
        )

    def test_leaderboard_deduplicates_repeated_runs_per_media(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self._make_booster(Path(tmp))
            b._update_leaderboard("gemini:romantic_lofi", "romantic_lofi", "Drop your 2 AM line", 4.0, 500, media_id="m1")
            b._update_leaderboard("gemini:romantic_lofi", "romantic_lofi", "Drop your 2 AM line", 8.0, 900, media_id="m1")
            b._update_leaderboard("gemini:romantic_lofi", "romantic_lofi", "Another banger", 10.0, 1200, media_id="m2")

            board = json.loads((Path(tmp) / "hook_leaderboard.json").read_text())
            rec = board["gemini:romantic_lofi"]
            self.assertEqual(rec["runs"], 2)
            self.assertEqual(rec["avg_engagement_pct"], 9.0)
            self.assertEqual(rec["best_views"], 1200)

    def test_smart_hook_reuses_winning_gemini_hook(self):
        with tempfile.TemporaryDirectory() as tmp:
            lb = Path(tmp) / "hook_leaderboard.json"
            lb.write_text(
                json.dumps(
                    {
                        "gemini:romantic_lofi": {
                            "niche": "romantic_lofi",
                            "avg_engagement_pct": 11.5,
                            "best_views": 4000,
                            "best_hook": "Who did you think of in the first 3 seconds? 🌙",
                        }
                    }
                )
            )
            with mock.patch.object(reels_booster.random, "random", return_value=0.1):
                hook, src = reels_booster.generate_smart_hook(
                    "Baarishein Anuv Jain cozy romance",
                    use_ai=False,
                    leaderboard_file=lb,
                )
            self.assertEqual(hook, "Who did you think of in the first 3 seconds? 🌙")
            self.assertEqual(src, "winner:romantic_lofi")

    def test_ban_shield_trips_and_blocks_next_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self._make_booster(Path(tmp))
            cl = mock.MagicMock()
            cl.user_id = "100"
            cl.user_medias.side_effect = RuntimeError("ChallengeRequired: checkpoint_required")

            ok = b.boost_latest_reel(cl, dry_run=False, ignore_sleep=True)
            self.assertFalse(ok)
            self.assertTrue(b.is_cooldown_active())

            # Subsequent run short-circuits safely without calling user_medias again
            cl.user_medias.reset_mock()
            ok_during_cd = b.boost_latest_reel(cl, dry_run=False, ignore_sleep=True)
            self.assertTrue(ok_during_cd)
            cl.user_medias.assert_not_called()

    def test_boost_latest_reel_records_radar_and_fan_requests(self):
        with tempfile.TemporaryDirectory() as tmp:
            b = self._make_booster(Path(tmp))
            cl = mock.MagicMock()
            cl.user_id = "999"
            media = SimpleNamespace(
                pk="55501",
                code="ReelX1",
                caption_text="Sahiba Crimson Manga Edit #sahiba",
                taken_at=datetime.now(timezone.utc) - timedelta(hours=1),
                play_count=6000,
                like_count=480,
                comment_count=30,
            )
            cl.user_medias.return_value = [media]
            cl.media_comment.return_value = SimpleNamespace(pk="c_own")
            cl.media_comments.return_value = [
                SimpleNamespace(
                    pk="c1",
                    user_id="201",
                    user=SimpleNamespace(username="fan_one"),
                    text="Please animate Samjho Na next song!",
                    has_liked_comment=False,
                ),
                SimpleNamespace(
                    pk="c2",
                    user_id="999",
                    user=SimpleNamespace(username="vynox_00000"),
                    text="Pinned comment",
                    has_liked_comment=False,
                ),
            ]

            with mock.patch.object(reels_booster, "generate_smart_hook", return_value=("Rate this frame 1-10 🩸", "template:crimson_manga")), mock.patch.object(
                reels_booster.time, "sleep", return_value=None
            ):
                ok = b.boost_latest_reel(cl, dry_run=False, max_likes=2, ignore_sleep=True)

            self.assertTrue(ok)
            analytics = json.loads((Path(tmp) / "reel_analytics.json").read_text())
            reqs = json.loads((Path(tmp) / "fan_requests.json").read_text())
            boosted = json.loads((Path(tmp) / "reels_boosted.json").read_text())
            self.assertEqual(analytics["55501"]["viral_tier"], "🔥 Breakout")
            self.assertEqual(len(reqs), 1)
            self.assertEqual(reqs[0]["author"], "fan_one")
            self.assertIn("55501", boosted)
            cl.comment_like.assert_called_once_with("c1")

    def test_generate_story_card_dimensions(self):
        with tempfile.TemporaryDirectory() as tmp:
            cover = Path(tmp) / "cover.jpg"
            out = Path(tmp) / "story_card.jpg"
            Image.new("RGB", (1080, 1920), (30, 10, 20)).save(cover)
            dest = reels_booster.generate_story_card(cover, "Baarishein - 2D Cozy Monsoon Romance", out_path=out)
            self.assertTrue(dest.exists())
            with Image.open(dest) as im:
                self.assertEqual(im.size, (1080, 1920))


class TestDuplicateGuard(unittest.TestCase):
    def test_registered_series_and_queued_songs_detected(self):
        for song in ("Baarishein", "Alag Aasmaan", "Waqt Ki Baatein", "Husn", "Choo Lo", "Kashish"):
            is_dup, reason = duplicate_guard.is_duplicate_song(song)
            self.assertTrue(is_dup, f"Expected {song} to be flagged as duplicate, got {reason}")

        is_dup, _ = duplicate_guard.is_duplicate_song("Completely Fresh Test Song 2099")
        self.assertFalse(is_dup)


class TestDailyDispatcherAndTrendProducer(unittest.TestCase):
    def test_trend_producer_skips_queued_duplicates_and_picks_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_file = Path(tmp) / "trend.log"
            with mock.patch.object(daily_trend_producer, "LOG_FILE", log_file):
                cand = daily_trend_producer.discover_next_trending()
            self.assertIsNotNone(cand)
            # Samjho Na and Ishq are now produced and queued in projects/queue/,
            # so the duplicate guard correctly advances to Kasoor by Prateek Kuhad.
            self.assertEqual(cand["id"], "kasoor")
            self.assertIn("Kasoor", log_file.read_text())

    def test_dispatcher_local_quota_and_duplicate_skip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qdir = root / "queue"
            adir = root / "archive"
            qdir.mkdir()
            adir.mkdir()
            log_file = root / "dispatcher.log"
            vid = root / "reel.mp4"
            vid.write_bytes(b"fake")
            qitem = qdir / "01_test.json"
            qitem.write_text(json.dumps({"title": "Test", "video_path": str(vid), "caption": "Hello world"}))

            fixed_now = datetime(2026, 11, 12, 19, 30, tzinfo=daily_dispatcher.IST)
            fake_dt_cls = mock.MagicMock()
            fake_dt_cls.now.return_value = fixed_now
            fake_dt_cls.fromisoformat.side_effect = datetime.fromisoformat

            with mock.patch.object(daily_dispatcher, "QUEUE_DIR", qdir), mock.patch.object(
                daily_dispatcher, "ARCHIVE_DIR", adir
            ), mock.patch.object(daily_dispatcher, "LOG_FILE", log_file), mock.patch.object(
                daily_dispatcher.datetime, "datetime", fake_dt_cls
            ), mock.patch.object(
                insta_local_post, "check_auth_health", return_value=(True, "SESSION_VALID", mock.MagicMock())
            ), mock.patch.dict(
                os.environ, {"GITHUB_ACTIONS": ""}, clear=False
            ), mock.patch(
                "subprocess.run"
            ), mock.patch(
                "duplicate_guard.is_duplicate_video", return_value=(True, "already published")
            ):
                ok = daily_dispatcher.dispatch_next(force=False)

            self.assertTrue(ok)
            self.assertFalse(qitem.exists())
            archived = list(adir.glob("*.json"))
            self.assertEqual(len(archived), 1)
            self.assertEqual(json.loads(archived[0].read_text())["status"], "skipped_duplicate")

    def test_dispatcher_publishes_reel_and_companion_story_card(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qdir = root / "queue"
            adir = root / "archive"
            qdir.mkdir()
            adir.mkdir()
            log_file = root / "dispatcher.log"
            vid = root / "reel.mp4"
            vid.write_bytes(b"fake_video_data")
            cover = root / "cover.jpg"
            Image.new("RGB", (1080, 1920), (20, 20, 40)).save(cover)
            qitem = qdir / "01_test.json"
            qitem.write_text(json.dumps({
                "title": "Samjho Na Test",
                "video_path": str(vid),
                "cover_path": str(cover),
                "caption": "Lovely aesthetic animation"
            }))

            fake_client = mock.MagicMock()
            fake_media = SimpleNamespace(code="C12345", pk="777001")
            fake_story = SimpleNamespace(pk="999001")

            with mock.patch.object(daily_dispatcher, "QUEUE_DIR", qdir), mock.patch.object(
                daily_dispatcher, "ARCHIVE_DIR", adir
            ), mock.patch.object(daily_dispatcher, "LOG_FILE", log_file), mock.patch.object(
                insta_local_post, "check_auth_health", return_value=(True, "SESSION_VALID", fake_client)
            ), mock.patch.object(
                insta_local_post, "upload_reel", return_value=fake_media
            ) as mock_upload_reel, mock.patch.object(
                insta_local_post, "upload_story", return_value=fake_story
            ) as mock_upload_story, mock.patch(
                "duplicate_guard.is_duplicate_video", return_value=(False, "")
            ), mock.patch(
                "duplicate_guard.register_video"
            ), mock.patch.object(
                fake_client, "user_medias", return_value=[]
            ), mock.patch(
                "youtube_uploader.check_auth_health", return_value=(False, "NO_CREDS", "")
            ), mock.patch.dict(
                os.environ, {"GITHUB_ACTIONS": ""}, clear=False
            ), mock.patch(
                "subprocess.run"
            ):
                ok = daily_dispatcher.dispatch_next(force=True)

            self.assertTrue(ok)
            mock_upload_reel.assert_called_once()
            mock_upload_story.assert_called_once()
            archived = list(adir.glob("*.json"))
            self.assertEqual(len(archived), 1)
            arch_data = json.loads(archived[0].read_text())
            self.assertEqual(arch_data["reel_url"], "https://www.instagram.com/reel/C12345/")
            self.assertTrue(arch_data.get("story_published"))
            self.assertEqual(arch_data.get("story_media_id"), "999001")
            self.assertIn("Story Promo Card live on Instagram Stories", log_file.read_text())

    def test_dispatcher_pauses_and_preserves_queue_on_auth_failure(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            qdir = root / "queue"
            adir = root / "archive"
            qdir.mkdir()
            adir.mkdir()
            log_file = root / "dispatcher.log"
            auth_status_file = root / "auth_status.json"
            vid = root / "reel.mp4"
            vid.write_bytes(b"fake")
            qitem = qdir / "04_romantic_baarishein.json"
            qitem.write_text(json.dumps({"title": "Baarishein", "video_path": str(vid), "caption": "Hello"}))

            with mock.patch.object(daily_dispatcher, "QUEUE_DIR", qdir), mock.patch.object(
                daily_dispatcher, "ARCHIVE_DIR", adir
            ), mock.patch.object(daily_dispatcher, "LOG_FILE", log_file), mock.patch.object(
                insta_local_post, "AUTH_STATUS_FILE", auth_status_file
            ), mock.patch.dict(
                os.environ, {"GITHUB_ACTIONS": "true"}, clear=False
            ), mock.patch.object(
                insta_local_post, "check_auth_health", return_value=(False, "SESSION_EXPIRED", "LoginRequired")
            ):
                ok = daily_dispatcher.dispatch_next(force=False)

            # Assert graceful pause and 100% queue preservation
            self.assertFalse(ok)
            self.assertTrue(qitem.exists(), "Queued reel MUST NOT be deleted on auth failure")
            self.assertEqual(len(list(adir.glob("*.json"))), 0, "No archive files should be created")
            self.assertIn("AUTHENTICATION HEALTH CHECK FAILED", log_file.read_text())
            self.assertIn("PRESERVING QUEUE", log_file.read_text())
            self.assertTrue(auth_status_file.exists())
            status_data = json.loads(auth_status_file.read_text())
            self.assertEqual(status_data["status"], "PAUSED_AUTH_REQUIRED")
            self.assertEqual(status_data["code"], "SESSION_EXPIRED")


class TestYouTubeUploader(unittest.TestCase):
    def test_youtube_build_ai_compliant_description(self):
        import youtube_uploader
        desc = youtube_uploader.build_ai_compliant_description(
            song_title="Baarishein",
            artist="Anuv Jain",
            custom_desc="Aesthetic monsoon memories.",
            tags=["#Monsoon", "#Romance"],
        )
        self.assertIn("TRANSPARENCY NOTICE", desc)
        self.assertIn("YouTube Synthetic Content Compliance", desc)
        self.assertIn("Vynox Autopilot Studio", desc)
        self.assertIn("Baarishein", desc)
        self.assertIn("Anuv Jain", desc)
        self.assertIn("#Shorts", desc)
        self.assertIn("#AIAnimation", desc)

    def test_youtube_upload_dry_run(self):
        import youtube_uploader
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_vid:
            result = youtube_uploader.upload_short(
                video_path=tmp_vid.name,
                title="Sahiba - Crimson Manga Edit",
                song_title="Sahiba",
                artist="Jasleen Royal",
                dry_run=True,
            )
            self.assertEqual(result["status"], "dry_run")
            self.assertIn("#Shorts", result["title"])

    def test_youtube_upload_longform_dry_run(self):
        import youtube_uploader
        with tempfile.NamedTemporaryFile(suffix=".mp4") as tmp_vid:
            result = youtube_uploader.upload_longform_video(
                video_path=tmp_vid.name,
                title="Late Night Drive 🌙 | Hindi Indie Slowed + Reverb",
                description="Chill mix with chapters",
                dry_run=True,
            )
            self.assertEqual(result["status"], "dry_run")
            self.assertIn("Late Night Drive", result["title"])
            self.assertNotIn("#Shorts", result["title"])


class TestDMAutoReplyAndCompilation(unittest.TestCase):
    def test_match_intent(self):
        import dm_auto_reply
        keywords = {
            "wallpaper": ["wallpaper", "wall", "4k photo"],
            "preset": ["preset", "cc", "lut"],
            "music_collab": ["collab", "promote", "promo"],
        }
        self.assertEqual(dm_auto_reply.match_intent("bhai wallpaper bhejo please", keywords), "wallpaper")
        self.assertEqual(dm_auto_reply.match_intent("which CC did you use? drop preset", keywords), "preset")
        self.assertEqual(dm_auto_reply.match_intent("want to collaborate for song promo", keywords), "music_collab")
        self.assertIsNone(dm_auto_reply.match_intent("random unrelated hello", keywords))

    def test_format_response(self):
        import dm_auto_reply
        template = "Here is wallpaper: {wallpaper_link} and email: {music_collab_email}"
        links = {
            "wallpaper_link": "https://drive.google.com/test",
            "music_collab_email": "vynox@test.com"
        }
        formatted = dm_auto_reply.format_response(template, links)
        self.assertIn("https://drive.google.com/test", formatted)
        self.assertIn("vynox@test.com", formatted)

    def test_sweep_funnel_comments_mock(self):
        import dm_auto_reply
        cl = mock.MagicMock()
        cl.user_id = "12345"
        cl.user_clips.return_value = [
            SimpleNamespace(
                pk="clip_1",
                code="Cl1pA",
                caption_text="Comment WALLPAPER for 4K art 📲"
            )
        ]
        cl.media_comments.return_value = [
            SimpleNamespace(
                pk="101",
                text="WALLPAPER please bro!!",
                user=SimpleNamespace(pk="99988", username="art_lover"),
            )
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_seen = Path(tmp) / "seen_comments.json"
            with mock.patch("dm_auto_reply.PROCESSED_COMMENTS_FILE", tmp_seen), \
                 mock.patch("dm_auto_reply.time.sleep", return_value=None):
                actions = dm_auto_reply.sweep_funnel_comments(cl=cl, dry_run=False, max_actions=2)

        self.assertEqual(actions, 1)
        cl.comment_like.assert_called_once_with(101)
        cl.media_comment.assert_called_once()
        cl.direct_send.assert_called_once()
        call_args = cl.direct_send.call_args
        self.assertEqual(call_args.kwargs.get("user_ids"), [99988])

    def test_compilation_builder_format_timestamp(self):
        import youtube_compilation_builder
        self.assertEqual(youtube_compilation_builder.format_timestamp(0), "00:00")
        self.assertEqual(youtube_compilation_builder.format_timestamp(75), "01:15")
        self.assertEqual(youtube_compilation_builder.format_timestamp(3665), "01:01:05")

    def test_friend_and_family_shield(self):
        import dm_auto_reply
        # Test blacklist of friends & family
        self.assertTrue(dm_auto_reply.is_friend_or_family("paras_kumar_thakur"))
        self.assertTrue(dm_auto_reply.is_friend_or_family("palak"))
        self.assertTrue(dm_auto_reply.is_friend_or_family("sarthak_brother"))
        self.assertTrue(dm_auto_reply.is_friend_or_family("tiwari_ji"))
        # Test following list VIP protection
        following = {"cool_creator_friend", "brother_99"}
        self.assertTrue(dm_auto_reply.is_friend_or_family("cool_creator_friend", following_set=following))
        # Random fan is NOT friend -> allowed for funnel
        self.assertFalse(dm_auto_reply.is_friend_or_family("random_fan_1234", following_set=following))

    def test_sleep_window_guard(self):
        import dm_auto_reply
        # 3:30 AM IST -> should be sleeping
        dt_night = datetime(2026, 11, 20, 3, 30)
        self.assertTrue(dm_auto_reply.is_sleep_window(dt_night))
        # 11:30 AM IST -> awake & active
        dt_day = datetime(2026, 11, 20, 11, 30)
        self.assertFalse(dm_auto_reply.is_sleep_window(dt_day))

    def test_trip_ban_shield_circuit_breaker(self):
        import dm_auto_reply
        with tempfile.TemporaryDirectory() as tmp:
            tmp_cooldown = Path(tmp) / "booster_cooldown.json"
            with mock.patch("dm_auto_reply.COOLDOWN_FILE", tmp_cooldown):
                dm_auto_reply.trip_ban_shield("challenge_required: mock test")
                self.assertTrue(tmp_cooldown.exists())
                data = json.loads(tmp_cooldown.read_text())
                self.assertTrue(data["active"])
                self.assertIn("challenge_required", data["reason"])


if __name__ == "__main__":
    unittest.main()
