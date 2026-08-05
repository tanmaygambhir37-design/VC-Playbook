# Deploying VC Playbook to Hugging Face Spaces

Why: HF Spaces keeps the app warm far longer than Streamlit Cloud's free tier,
and cold-wakes in seconds instead of 30+. The config is already in this repo
(the frontmatter block at the top of `README.md` tells HF it's a Streamlit app,
entry point `app/app.py`, Python 3.12).

You do the account + push steps below (I can't create accounts or handle your
token). It's ~5 minutes, one time.

## 1. Create the Space
1. Sign up / log in at https://huggingface.co (free, no card).
2. Top-right → **New** → **Space**.
3. Fill in:
   - **Owner:** your username
   - **Space name:** `vc-playbook`
   - **License:** MIT
   - **SDK:** **Streamlit**
   - **Hardware:** CPU basic (free)
   - **Visibility:** Public
4. Click **Create Space**. It starts with a placeholder app — we'll overwrite it.

## 2. Get a write token
1. https://huggingface.co/settings/tokens → **New token** → Type **Write** → create.
2. Copy it. You'll paste it as the *password* when git prompts (username = your HF username).

## 3. Push this repo to the Space
From the repo folder in your terminal:

```bash
git remote add hf https://huggingface.co/spaces/<your-username>/vc-playbook
git push hf main:main
```

When prompted: username = your HF username, password = the write token from step 2.
(The Space repo starts with its own README/app; if git refuses, run
`git push hf main:main --force` — you're intentionally replacing the placeholder.)

## 4. Secrets (only if you use the Formspree usage ping)
Space → **Settings** → **Variables and secrets** → add `FORMSPREE_URL` with your
Formspree endpoint. HF injects it the same way Streamlit Cloud does.

## 5. It's live
Build takes 1-3 min (watch the **Logs** tab). Your public URL is:
```
https://<your-username>-vc-playbook.hf.space
```
Update your Portfolio, LinkedIn, and CV links to that URL.

## Keeping it from ever sleeping (optional)
HF free CPU Spaces can still nap after ~48h of zero traffic (but wake in
seconds). To make it truly always-on, create a free https://uptimerobot.com
monitor that pings your `.hf.space` URL every 5 minutes.

## Updating it later
Same as GitHub — I (or you) just `git push hf main:main`. To push both remotes
at once you can add HF as a second push URL on `origin`:
```bash
git remote set-url --add --push origin https://github.com/tanmaygambhir37-design/VC-Playbook.git
git remote set-url --add --push origin https://huggingface.co/spaces/<your-username>/vc-playbook
```
Then a single `git push origin main` updates GitHub and redeploys HF.

## If the build fails on sdk_version
If the log complains `1.40.0` isn't a valid Streamlit version for Spaces, it
prints the allowed values — bump `sdk_version` in `README.md`'s frontmatter to
one it lists and push again.
