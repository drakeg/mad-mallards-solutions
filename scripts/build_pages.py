"""Build a static, non-collecting GitHub Pages preview from the full-stack site.

Usage:
    python3 scripts/build_pages.py
    python3 scripts/build_pages.py --prefix /mad-mallards-solutions
"""
from __future__ import annotations
import argparse
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "site"
OUTPUT = ROOT / "dist"

def build(prefix: str = "/mad-mallards-solutions") -> None:
    prefix = "/" + prefix.strip("/") if prefix.strip("/") else ""
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    shutil.copytree(SITE, OUTPUT)
    (OUTPUT / ".nojekyll").write_text("")
    for file in OUTPUT.rglob("*.html"):
        text = file.read_text(encoding="utf-8")
        if file.name == "index.html" and file.parent == OUTPUT:
            contact = '''<div id="contact-form" class="form-card static-callout" role="note"><h3>Contact form coming soon</h3><p>This is a temporary GitHub Pages preview. Messages cannot be submitted from this preview yet. Contact submissions work in the local version, and this section will be enabled when secure hosting is connected.</p><a class="underlink" href="''' + '''/blog/">Explore the journal ↗</a></div>'''
            signup = '''<div id="subscribe-form" class="subscribe-form static-callout" role="note"><h3>Newsletter signup coming soon</h3><p>Subscriptions are not collected on this temporary preview. The signup will be enabled when a secure backend and confirmation emails are connected.</p><a class="underlink" href="''' + '''/blog/">Read the journal ↗</a></div>'''
            text, contacts = re.subn(r'<form\s+id="contact-form".*?</form>', lambda _:contact, text, count=1, flags=re.DOTALL)
            text, subscribers = re.subn(r'<form\s+id="subscribe-form".*?</form>', lambda _:signup, text, count=1, flags=re.DOTALL)
            if contacts != 1 or subscribers != 1:
                raise RuntimeError("Contact or subscription form missing; refuse unsafe Pages build")
        # Do not let a temporary preview compete with the production domain in search.
        text = text.replace("<head>", '<head><meta name="robots" content="noindex,nofollow">', 1)
        if file.name == "privacy.html":
            text = text.replace("This prototype stores the name, email address, and message you submit through the contact form, and email addresses submitted to subscribe.", "This temporary GitHub Pages preview does not accept or store contact or subscription submissions.")
            text = text.replace("Records are stored in a server-side SQLite database for follow-up. If the operator enables SMTP notifications, contact messages are also forwarded to the configured email provider and inbox.", "The separate local version can store submissions in SQLite; its data is not used by this GitHub Pages preview.")
        # Path rewriting happens only in HTML attributes. Leave fragment links alone.
        text = re.sub(r'((?:href|src|action)="/)([^"]*)"', lambda match: match.group(1)[:-1] + prefix + "/" + match.group(2) + '"', text)
        file.write_text(text, encoding="utf-8")
    app = OUTPUT / "app.js"
    js = app.read_text(encoding="utf-8")
    js, count = re.subn(r'for \(const id of \[\x27contact\x27,\x27subscribe\x27\]\).*$', '', js, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError("Expected dynamic form handler missing; refuse Pages build")
    app.write_text(js, encoding="utf-8")
    with (OUTPUT / "styles.css").open("a", encoding="utf-8") as style:
        style.write("\n/* GitHub Pages preview: static, no lead collection */\n.static-callout h3{font:700 23px/1.35 Manrope,sans-serif;margin:0 0 12px}.static-callout p{font-size:14px;line-height:1.8;color:inherit;margin:0 0 18px}.static-callout .underlink{display:inline-block}.subscribe-form.static-callout{border:1px solid #89a99a;padding:35px;background:#24493e}.static-callout a{color:inherit}\n")
    print(f"Built Pages preview: {OUTPUT} (prefix: {prefix or '/'})")

if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--prefix", default="/mad-mallards-solutions")
    args = cli.parse_args()
    build(args.prefix)
