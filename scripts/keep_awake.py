"""Keep the Streamlit Community Cloud app awake.

A plain HTTP GET does NOT work: Streamlit returns a static HTML shell (200)
without launching the app, and its sleep timer counts real browser sessions,
not HTTP hits. So we open the app in a headless browser (Playwright/Chromium),
which runs the JS and establishes the WebSocket session that resets the timer.
If the app is already asleep, we click its "wake up" button.

Run on a GitHub Actions cron every 6 hours (Streamlit sleeps after ~12h idle).
"""

import sys

from playwright.sync_api import sync_playwright

APP_URL = "https://vc-lab-5mg6vkhrt7uucrxjnowfe3.streamlit.app/"
WAKE_BUTTON = "Yes, get this app back up!"


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(APP_URL, wait_until="domcontentloaded", timeout=60_000)

        # If the sleep screen is up, click the wake button.
        try:
            button = page.get_by_text(WAKE_BUTTON, exact=False)
            if button.count() > 0:
                print("App was asleep — clicking wake button.")
                button.first.click()
                page.wait_for_timeout(45_000)  # let it boot
            else:
                print("App was already awake.")
        except Exception as exc:  # noqa: BLE001 — best-effort waker
            print(f"Wake-button check skipped: {exc}")

        # Hold the session open briefly so it registers as real activity.
        page.wait_for_timeout(15_000)
        title = page.title()
        browser.close()
        print(f"Session established. Page title: {title!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
