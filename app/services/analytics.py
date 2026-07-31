"""analytics.py — pageview and funnel instrumentation.

Every function here is a no-op unless configured, so the app runs identically
with nothing attached. Configure any subset in Streamlit secrets:

    GOATCOUNTER_CODE  = "vcplaybook"       # -> vcplaybook.goatcounter.com
    PLAUSIBLE_DOMAIN  = "vcplaybook.com"
    UMAMI_URL         = "https://analytics.example.com"
    UMAMI_WEBSITE_ID  = "0000-0000"
    EVENT_WEBHOOK_URL = "https://..."      # funnel events, server-side POST

Pageviews are sent from the browser (Streamlit strips <script> from markdown,
so they ride in a zero-height components iframe). Funnel events are sent from
Python, off-thread, so a slow endpoint never blocks a rerun.

With nothing configured at all, events still print to stdout — which shows up
in the Streamlit Cloud log viewer. That is the zero-setup way to see whether
anyone is getting past the landing page.
"""

import json
import threading
import urllib.parse
import uuid
from datetime import datetime, timezone

import requests
import streamlit as st
import streamlit.components.v1 as components

_TIMEOUT = 4


def _secret(key: str, default: str = "") -> str:
    """Secrets lookup that survives having no secrets.toml at all."""
    try:
        return str(st.secrets.get(key, default))
    except Exception:
        return default


def _flag(key: str, default: bool) -> bool:
    raw = _secret(key, "").strip().lower()
    if not raw:
        return default
    return raw in {"1", "true", "yes", "on"}


def session_id() -> str:
    """Stable per-browser-session id so events can be stitched into a funnel."""
    if "_vcl_session" not in st.session_state:
        st.session_state["_vcl_session"] = uuid.uuid4().hex[:12]
    return st.session_state["_vcl_session"]


# ------------------------------------------------------------------ pageviews


def _pageview_html(path: str, title: str) -> str:
    """Browser-side beacons for whichever providers are configured."""
    beacons = []

    goatcounter = _secret("GOATCOUNTER_CODE")
    if goatcounter:
        query = urllib.parse.urlencode({"p": path, "t": title})
        beacons.append(
            f'<img src="https://{goatcounter}.goatcounter.com/count?{query}" '
            'alt="" style="position:absolute;width:1px;height:1px;border:0">'
        )

    plausible = _secret("PLAUSIBLE_DOMAIN")
    if plausible:
        payload = json.dumps({
            "name": "pageview",
            "domain": plausible,
            "url": f"https://{plausible}{path}",
        })
        beacons.append(
            "<script>fetch('https://plausible.io/api/event',{method:'POST',"
            "headers:{'Content-Type':'application/json'},"
            f"body:{json.dumps(payload)}}}).catch(function(){{}});</script>"
        )

    umami_url = _secret("UMAMI_URL").rstrip("/")
    umami_id = _secret("UMAMI_WEBSITE_ID")
    if umami_url and umami_id:
        payload = json.dumps({
            "type": "event",
            "payload": {"website": umami_id, "url": path, "title": title},
        })
        beacons.append(
            f"<script>fetch('{umami_url}/api/send',{{method:'POST',"
            "headers:{'Content-Type':'application/json'},"
            f"body:{json.dumps(payload)}}}).catch(function(){{}});</script>"
        )

    return "".join(beacons)


def track_page(page: str, title: str = "") -> None:
    """Record one pageview per page per session.

    Streamlit reruns the whole script on every widget interaction, so without
    the session guard a single visitor moving three sliders would look like
    four pageviews.
    """
    marker = f"_vcl_pv_{page}"
    if st.session_state.get(marker):
        return
    st.session_state[marker] = True

    path = page if page.startswith("/") else f"/{page}"
    markup = _pageview_html(path, title or page)
    if markup:
        components.html(markup, height=0)
    track_event("pageview", page=page)


# --------------------------------------------------------------------- events


def _post(url: str, payload: dict) -> None:
    try:
        requests.post(url, json=payload, timeout=_TIMEOUT)
    except Exception:
        pass


def track_event(name: str, once_per_session: bool = False, **props) -> None:
    """Record a funnel event.

    `once_per_session` is for milestones you only want counted once per
    visitor (first screening run), as opposed to repeatable actions.
    """
    if once_per_session:
        marker = f"_vcl_ev_{name}"
        if st.session_state.get(marker):
            return
        st.session_state[marker] = True

    payload = {
        "event": name,
        "session": session_id(),
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        **{k: v for k, v in props.items() if v is not None},
    }

    if _flag("LOG_EVENTS", True):
        print(f"[vcl-event] {json.dumps(payload, default=str)}", flush=True)

    webhook = _secret("EVENT_WEBHOOK_URL") or _secret("FORMSPREE_URL")
    if webhook:
        threading.Thread(target=_post, args=(webhook, payload), daemon=True).start()

    trail = st.session_state.setdefault("_vcl_events", [])
    trail.append(payload)
    del trail[:-200]  # keep the session trail bounded
