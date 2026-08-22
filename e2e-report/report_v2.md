# E2E v2 Report

| Step | Status | Detail |
|---|---|---|
| ✅ wizard-appare | OK | url=http://127.0.0.1:22998/setup — WIZARD APPARE ✓ |
| ✅ setup-step1-visible | OK |  |
| ⚠️ setup-step2-fill | WARN | 0 campi compilati |
| ✅ setup-complete | OK | url dopo=http://127.0.0.1:22998/ |
| ✅ tab-home | OK |  |
| ✅ home-grid | OK | 5 cards |
| ✅ home-toolbar | OK |  |
| ✅ home-digest | OK |  |
| ✅ tab-picker | OK |  |
| ✅ tab-library | OK |  |
| ✅ tab-courses | OK |  |
| ✅ tab-plan | OK |  |
| ✅ plan-generate | OK |  |
| ✅ plan-fold | OK | expanded=true |
| ✅ plan-versions-btn | OK |  |
| ✅ plan-ai-panel | OK |  |
| ✅ tab-analysis | OK |  |
| ✅ analysis-chartjs | OK |  |
| ⚠️ analysis-painted | WARN | 0/1 dipinti |
| ✅ tab-dfa | OK |  |
| ✅ tab-settings | OK |  |
| ✅ settings-icu-text | OK |  |
| ✅ settings-api-field | OK | 3 campi |
| ✅ tab-hrv | OK |  |
| ✅ tab-nutrition | OK |  |
| ✅ tab-bia | OK |  |
| ✅ tab-profile | OK |  |
| ✅ tab-whatsnew | OK |  |
| ✅ tab-ai_coach | OK |  |
| ✅ api-FTP | OK | HTTP 200 |
| ✅ api-Nutrition | OK | HTTP 200 |
| ✅ api-Fueling | OK | HTTP 200 |
| ✅ api-PowerCurve | OK | HTTP 200 |
| ✅ api-CPModels | OK | HTTP 200 |
| ✅ api-Readiness | OK | HTTP 200 |
| ❌ api-HRV-summary | FAIL | HTTP 404 |
| ✅ api-Digest | OK | HTTP 200 |
| ✅ api-PlanVersions | OK | HTTP 200 |
| ✅ api-AIStatus | OK | HTTP 200 |
| ✅ api-SyncStatus | OK | HTTP 200 |
| ✅ api-Wellness | OK | HTTP 200 |
| ✅ api-Rides | OK | HTTP 200 |
| ✅ api-OnboardingStatus | OK | HTTP 200 |
| ✅ api-ExportBackup | OK | HTTP 200 |
| ✅ api-TerraStatus | OK | HTTP 200 |
| ✅ api-WorkoutsClassify | OK | HTTP 200 |
| ✅ tema-dark | OK |  |
| ✅ layout-edit | OK | edit=True, handle=5 |
| ⚠️ nav-today->plan | WARN | Page.evaluate: SyntaxError: Unexpected token ')'
    at eval |

## Console errors (1)
- Failed to load resource: the server responded with a status of 404 (Not Found)

## Page errors (0)

## Network (1)
- 404 http://127.0.0.1:22998/api/hrv/summary
