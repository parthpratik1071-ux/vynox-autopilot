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
    def test_trend_producer_picks_samjho_na_next(self):
        with tempfile.TemporaryDirectory() as tmp:
            log_file = Path(tmp) / "trend.log"
            with mock.patch.object(daily_trend_producer, "LOG_FILE", log_file):
                cand = daily_trend_producer.discover_next_trending()
            self.assertIsNotNone(cand)
            self.assertEqual(cand["id"], "samjho_na")
            self.assertIn("Samjho Na", log_file.read_text())

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

            fixed_now = datetime(2026, 11, 12, 14, 30, tzinfo=daily_dispatcher.IST)
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


if __name__ == "__main__":
    unittest.main()
