# E2E Test Report

| Step | Status | Detail |
|------|--------|--------|
| ✅ primo-avvio | OK | url=http://127.0.0.1:22999/setup |
| ✅ wizard-appare | OK | redirect a http://127.0.0.1:22999/setup |
| ✅ setup-render | OK | 10 input, 14 buttons |
| ❌ FATAL | FAIL | Error: Locator.is_visible: Error: strict mode violation: locator("#ob-next, button:has-text(\"Avanti\"), button:has-text(\"Next\")") resolved to 2 elements:
    1) <button type="button" id="step2-next" onclick="nextStep(3)" class="btn btn-primary">Next</button> aka locator("#step2-next")
    2) <button type="button" onclick="nextStep(4)" class="btn btn-primary">Next</button> aka locator("#step-3").get_by_text("Next")

Call log:
    - checking visibility of locator("#ob-next, button:has-text(\"Avanti\"), button:has-text(\"Next\")")
 |

## Console errors (0)

## Page errors (0)

## Network failures (0)
