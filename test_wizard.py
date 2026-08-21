#!/usr/bin/env python3
"""Verifica wizard /setup: rendering + JS errors."""
import sys
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

with sync_playwright() as p:
    b = p.chromium.connect_over_cdp("http://127.0.0.1:9222")
    ctx = b.contexts[0]
    page = ctx.new_page()
    errs = []
    page.on("pageerror", lambda e: errs.append(str(e)))
    page.goto("http://127.0.0.1:22400/setup", wait_until="domcontentloaded", timeout=30000)
    page.wait_for_timeout(3000)
    title = page.title()
    body_len = len(page.content())
    # elementi chiave del wizard
    has_form = page.locator('form, .wizard, [class*=wizard], [id*=wizard], input').count()
    print(f"titolo: {title}")
    print(f"html bytes: {body_len}, input/form elements: {has_form}")
    print(f"pageerror: {errs[:5] if errs else 'nessuno'}")
    page.close()
    b.close()
