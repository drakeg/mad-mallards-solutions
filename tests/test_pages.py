"""Verify static Pages output cannot accidentally collect leads or break links."""
import re
import unittest
from pathlib import Path
from scripts.build_pages import build, OUTPUT, SITE

BASE = "/mad-mallards-solutions"

class GitHubPagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        build(BASE)

    def test_copy_complete(self):
        for path in ("index.html", "styles.css", "scrollcraft.js", "app.js", "assets/mark.svg",
                     "blog/index.html", "blog/automation-without-the-hype.html",
                     "blog/small-business-cloud.html", "blog/monitoring-what-matters.html",
                     "privacy.html", ".nojekyll"):
            with self.subTest(path=path):
                self.assertTrue((OUTPUT / path).is_file())

    def test_project_relative_asset_links_resolve(self):
        for file in OUTPUT.rglob("*.html"):
            html = file.read_text()
            for dest in re.findall(r'(?:href|src)="(/[^"]*)"', html):
                if not dest.startswith(BASE):
                    self.fail(f"{file}: link escapes GitHub Pages prefix: {dest}")
                rel = dest[len(BASE):].split("#", 1)[0].split("?", 1)[0].lstrip("/")
                local = OUTPUT / rel
                with self.subTest(file=str(file.relative_to(OUTPUT)), link=dest):
                    self.assertTrue(local.is_file() or (local / "index.html").is_file())

    def test_static_preview_does_not_accept_submission(self):
        home = (OUTPUT / "index.html").read_text()
        app = (OUTPUT / "app.js").read_text()
        self.assertNotIn('<form', home)
        self.assertNotIn('/api/contact', home)
        self.assertNotIn('/api/subscribe', home)
        self.assertNotIn('fetch(form.action', app)
        self.assertIn('Contact form coming soon', home)
        self.assertIn('Newsletter signup coming soon', home)
        self.assertIn('id="contact"', home)
        self.assertIn('id="subscribe"', home)

    def test_local_fullstack_stays_intact(self):
        full_site = (SITE / "index.html").read_text()
        self.assertIn('action="/api/contact"', full_site)
        self.assertIn('action="/api/subscribe"', full_site)

    def test_noindex_for_temporary_preview(self):
        for file in OUTPUT.rglob("*.html"):
            self.assertIn('name="robots" content="noindex,nofollow"', file.read_text())
