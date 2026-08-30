"""Visual smoke test: catches regressions in page styling.

Fails if any page renders with the browser-default font (Times New Roman)
or a transparent/black body background — the signature of a missing/
unloaded CSS (the bug fixed in chore/ui-consistency).

Run against a running server:
  CPSL_PORT=22400 python tests/visual_smoke.py
Requires playwright + chromium installed.
"""
import os
import sys
import glob
import urllib.request
from playwright.sync_api import sync_playwright

BASE = f"http://127.0.0.1:{os.environ.get('CPSL_PORT', '22400')}"
PAGES = ["/", "/hrv_monitor", "/profile_setup", "/player", "/setup"]

# A page is "broken" if the body falls back to the browser default font (Times New Roman)


def main():
    # locate chromium
    pw_dir = os.path.join(os.environ.get("LOCALAPPDATA", ""), "ms-playwright")
    chrome = glob.glob(os.path.join(pw_dir, "chromium-*/chrome-win64/chrome.exe"))
    exe = chrome[0] if chrome else None

    failures = []
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=exe)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        for path in PAGES:
            try:
                code = urllib.request.urlopen(BASE + path, timeout=15).status
            except Exception as e:  # noqa: BLE001
                failures.append(f"{path}: HTTP error {e}")
                continue
            if code != 200:
                failures.append(f"{path}: HTTP {code} (expected 200)")
                continue
            page.goto(BASE + path, wait_until="networkidle", timeout=20000)
            info = page.evaluate(
                "() => { const cs = getComputedStyle(document.body);"
                " return { bg: cs.backgroundColor, font: cs.fontFamily.toLowerCase() }; }"
            )
            # A broken page falls back to the browser default serif. Our app uses
            # Inter / system-ui / sans-serif everywhere, so a default serif
            # (Times New Roman) or a bare "serif" token means CSS didn't load.
            # Note: "sans-serif" is fine — only the bare "serif" fallback is bad.
            font = info["font"]
            broken_font = ("times new roman" in font) or (
                "serif" in font and "sans-serif" not in font
            )
            if broken_font:
                failures.append(f"{path}: bad font '{font}' (CSS not applied)")
            if info["bg"] in ("rgba(0, 0, 0, 0)", "transparent"):
                failures.append(f"{path}: transparent body bg (CSS not applied)")
        browser.close()

    if failures:
        print("VISUAL SMOKE FAILED:")
        for f in failures:
            print("  -", f)
        sys.exit(1)
    print(f"VISUAL SMOKE OK: {len(PAGES)} pages styled correctly (Inter/system font, real bg).")
    sys.exit(0)


if __name__ == "__main__":
    main()
