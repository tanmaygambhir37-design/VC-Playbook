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

# ?keepalive=1 tells the app this is the bot, so it skips analytics and the A/B
# experiment — automated wake-ups never pollute the funnel data.
APP_URL = "https://vcplaybook.streamlit.app/?keepalive=1"
# The old address is still on resumes and portfolio links; keep it awake too so
# those visitors reach the "we've moved" page instead of a sleep screen.
LEGACY_URL = "https://vc-lab-5mg6vkhrt7uucrxjnowfe3.streamlit.app/?keepalive=1"
WAKE_BUTTON = "Yes, get this app back up!"


def wake(browser, url: str) -> None:
    page = browser.new_page()
    page.goto(url, wait_until="domcontentloaded", timeout=60_000)

    # If the sleep screen is up, click the wake button.
    try:
        button = page.get_by_text(WAKE_BUTTON, exact=False)
        if button.count() > 0:
            print(f"{url}: asleep, clicking wake button.")
            button.first.click()
            page.wait_for_timeout(45_000)  # let it boot
        else:
            print(f"{url}: already awake.")
    except Exception as exc:  # noqa: BLE001 — best-effort waker
        print(f"{url}: wake-button check skipped: {exc}")

    # Hold the session open briefly so it registers as real activity.
    page.wait_for_timeout(15_000)
    print(f"{url}: session established. Page title: {page.title()!r}")
    page.close()


def main() -> int:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for url in (APP_URL, LEGACY_URL):
            wake(browser, url)
        browser.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
