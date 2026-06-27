import os
import sys
import unittest
from unittest.mock import patch, MagicMock
from urllib.parse import quote_plus

# Import functions from the main tool
from gitdorker_elite import make_browser_url, load_dorks

class TestGitDorkerElite(unittest.TestCase):

    # ── make_browser_url ─────────────────────────────────────────────
    def test_make_browser_url_basic(self):
        url = make_browser_url("example.com", "api_key")
        expected = f"https://github.com/search?q={quote_plus('example.com')}+{quote_plus('api_key')}&type=code"
        self.assertEqual(url, expected)

    def test_make_browser_url_with_special_chars(self):
        url = make_browser_url("test.com", "filename:.env")
        self.assertIn("filename%3A.env", url)

    # ── load_dorks ──────────────────────────────────────────────────
    def test_load_dorks_valid_file(self):
        dorks = load_dorks("dorks.txt")
        self.assertIsInstance(dorks, list)
        self.assertGreater(len(dorks), 0)

    def test_load_dorks_skips_comments(self):
        dorks = load_dorks("dorks.txt")
        for dork in dorks:
            self.assertFalse(dork.startswith("#"))

    def test_load_dorks_non_existent_file(self):
        with self.assertRaises(SystemExit):
            load_dorks("this_file_does_not_exist.txt")


if __name__ == "__main__":
    unittest.main()
