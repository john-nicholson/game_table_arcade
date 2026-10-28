"""Deployment and download failure checks; uses an isolated temporary home."""

import contextlib
import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("arcade", ROOT / "scripts/arcade.py")
arcade = importlib.util.module_from_spec(spec)
spec.loader.exec_module(arcade)


class ArcadeTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="game-table-test-")
        self.addCleanup(self.temporary.cleanup)
        self.home = Path(self.temporary.name)
        self.config = self.home / ".config/game-table"
        self.state = self.home / ".local/state/game-table"
        self.data = self.home / "Games/table with spaces"
        self.config.mkdir(parents=True)
        self.save_settings({"data_dir": str(self.data)})
        for name, value in (("HOME", self.home), ("CONFIG", self.config), ("STATE", self.state)):
            p = patch.object(arcade, name, value)
            p.start()
            self.addCleanup(p.stop)
        p = patch.object(arcade, "find_core", return_value=Path("/usr/lib/test/libretro/nestopia_libretro.so"))
        p.start()
        self.addCleanup(p.stop)
        self.output = contextlib.redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def save_settings(self, values):
        (self.config / "settings.json").write_text(json.dumps(values))

    def test_reconfigure_preserves_bindings_backs_up_changes_and_is_idempotent(self):
        config = self.config / "retroarch.cfg"
        original = '# Local control layout\ninput_player1_a_btn = "4"\nvideo_fullscreen = "false"\n'
        config.write_text(original)
        arcade.configure()
        configured = config.read_text()
        self.assertIn('input_player1_a_btn = "4"', configured)
        self.assertIn('video_fullscreen = "true"', configured)
        backups = list((self.state / "backups").rglob("retroarch.cfg"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), original)
        arcade.configure()
        self.assertEqual(config.read_text(), configured)
        self.assertEqual(list((self.state / "backups").rglob("retroarch.cfg")), backups)

    def test_playlist_uses_absolute_paths_and_includes_local_games(self):
        arcade.configure()
        rom = self.data / "roms/nes/My local game.nes"
        rom.write_bytes(b"NES\x1a")
        arcade.configure()
        playlist = json.loads((self.data / "playlists/Free Homebrew.lpl").read_text())
        self.assertEqual(playlist["items"][0]["path"], str(rom))
        self.assertEqual(playlist["items"][0]["label"], "My local game")
        self.assertEqual(playlist["items"][0]["core_name"], "Nestopia")

    def test_rejects_invalid_settings_before_writing_config(self):
        for values in ({"display_rotation": "sideways"},
                       {"player1_index": 1, "player2_index": 1},
                       {"data_dir": "relative/path"}):
            with self.subTest(values=values):
                self.save_settings(values)
                with self.assertRaises(ValueError):
                    arcade.configure()
                self.assertFalse((self.config / "retroarch.cfg").exists())

    def test_backup_supports_external_data_directory(self):
        external = self.home / "external-mount"
        external.mkdir()
        # Treat only a child of this temp tree as HOME, leaving target outside it.
        with patch.object(arcade, "HOME", self.home / "user-home"):
            target = external / "SOURCES.json"
            arcade.write_managed(target, "old")
            arcade.write_managed(target, "new")
        backups = list((self.state / "backups").rglob("SOURCES.json"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "old")

    def game(self, content):
        return {"title": "Test game", "filename": "test.nes", "url": "https://example.org/test.nes",
                "sha256": hashlib.sha256(content).hexdigest()}

    def response(self, content):
        response = io.BytesIO(content)
        response.url = "https://example.org/test.nes"
        return response

    def test_download_verifies_and_reuses_existing_rom(self):
        content = b"NES\x1a" + bytes(32)
        game = self.game(content)
        with patch.object(arcade.urllib.request, "urlopen", return_value=self.response(content)) as request:
            arcade.download_game(game, self.data_parent())
            arcade.download_game(game, self.data)
            request.assert_called_once()
        self.assertEqual((self.data / "test.nes").read_bytes(), content)

    def data_parent(self):
        self.data.mkdir(parents=True, exist_ok=True)
        return self.data

    def test_download_bad_hash_and_interruption_leave_no_partial_rom(self):
        directory = self.data_parent()
        game = self.game(b"NES\x1aexpected")
        with patch.object(arcade.urllib.request, "urlopen", return_value=self.response(b"bad")):
            with self.assertRaisesRegex(ValueError, "SHA-256 mismatch"):
                arcade.download_game(game, directory)
        self.assertEqual(list(directory.iterdir()), [])
        response = self.response(b"unused")
        with patch.object(response, "read", side_effect=OSError("connection lost")):
            with patch.object(arcade.urllib.request, "urlopen", return_value=response):
                with self.assertRaisesRegex(OSError, "connection lost"):
                    arcade.download_game(game, directory)
        self.assertEqual(list(directory.iterdir()), [])

    def test_conflicting_rom_is_not_overwritten(self):
        directory = self.data_parent()
        target = directory / "test.nes"
        target.write_bytes(b"personal version")
        with patch.object(arcade.urllib.request, "urlopen") as request:
            with self.assertRaisesRegex(ValueError, "Existing ROM differs"):
                arcade.download_game(self.game(b"new version"), directory)
            request.assert_not_called()
        self.assertEqual(target.read_bytes(), b"personal version")

    def test_shell_syntax(self):
        for path in [ROOT / "install.sh", *(ROOT / "scripts").glob("*.sh"),
                     ROOT / "scripts/game-table", ROOT / "scripts/game-table-session"]:
            with self.subTest(path=path.name):
                subprocess.run(["bash", "-n", str(path)], check=True)

    def test_runtime_deployment_installs_independent_cli_and_preserves_settings(self):
        app = self.home / ".local/share/game-table/app"
        original = (self.config / "settings.json").read_text()
        arcade.deploy(ROOT, app)
        arcade.deploy(ROOT, app)
        wrapper = self.home / ".local/bin/game-table"
        result = subprocess.run([str(wrapper), "--help"], env={**os.environ, "HOME": str(self.home)},
                                capture_output=True, text=True, check=True, cwd=self.home)
        self.assertIn("configure|download|doctor|launch", result.stdout)
        self.assertEqual((self.config / "settings.json").read_text(), original)
        self.assertTrue((app / "scripts/arcade.py").is_file())
        self.assertTrue((app / "config/i3.conf").is_file())
        self.assertFalse((self.state / "backups").exists())

    @unittest.skipUnless(os.environ.get("GAME_TABLE_NETWORK_TEST") == "1", "opt-in real download check")
    def test_live_catalogue_download_and_playlist(self):
        arcade.download()
        arcade.download()  # Offline reuse path for each downloaded file.
        for game in arcade.catalogue():
            self.assertEqual(arcade.digest(self.data / "roms/nes" / game["filename"]), game["sha256"])
        playlist = json.loads((self.data / "playlists/Free Homebrew.lpl").read_text())
        self.assertEqual(len(playlist["items"]), len(arcade.catalogue()))
        self.assertTrue((self.data / "SOURCES.json").is_file())


if __name__ == "__main__":
    unittest.main()
