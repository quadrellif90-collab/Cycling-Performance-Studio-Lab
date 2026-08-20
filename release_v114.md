# Cycling Performance Studio Lab v1.1.4

**UI fixes + new icon.** Two regressions from the v1.0.2 tab-configurator work are resolved, plus a fresh app icon.

## Fixed
### 🖱️ Tabs now open on click
The dynamic tab renderer rebuilt the bar with `innerHTML = ''`, which dropped the click listeners — so clicking a tab did nothing. Reverted to static tabs in the markup and a lightweight `applyTabVisibility()` that only toggles `display`. Click handlers stay attached; tabs open correctly. The per-profile show/hide configurator still works.

### 🔗 Intervals.icu "Connect" (login) now works
The API-Key connect path posted the wrong field names (`api_key`/`athlete_id`) to the save endpoint, which expects `icu_api_key`/`icu_id` — so the connection silently failed. Corrected in `connectIcuApiKey()`. Verified live:
- `test-icu` → ok (athlete detected)
- `save` → `creds_test: passed`
- `connection` → `connected: true, method: apikey, write_ok: true`

## Changed
- **New app icon** — racing-gradient disc with a cycling wheel, an analytics line chart and a lightning bolt. Bundled as `assets/icon.ico` (Windows/Linux) and `icon_512x512.png`.

## Notes
- The OAuth "Connect" button still requires a registered client secret not bundled in this build — use **API Key** (Settings → Connections → "Connetti con API Key"). This is the supported path.

## Download
| Platform | Asset |
|----------|-------|
| Windows  | `CyclingPerformanceStudioLab.exe` |
| macOS    | `Cycling-Performance-Studio-Lab.dmg` / `-macOS.tar.gz` |
| Linux    | `CyclingPerformanceStudioLab-v1.1.4-linux-x86_64.tar.gz` |
