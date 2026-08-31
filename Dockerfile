# Runs VC Playbook as a 24/7 container on Railway / Render / Fly.io / Koyeb /
# Cloud Run. Streamlit Community Cloud ignores this file, so it's harmless there.
FROM python:3.12-slim

WORKDIR /app

# System deps kept minimal; curl is only for the healthcheck.
RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hosts inject the port via $PORT; default to 8501 for local `docker run`.
ENV PORT=8501
EXPOSE 8501

HEALTHCHECK --interval=30s --timeout=5s --start-period=40s \
  CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Shell form so ${PORT} expands at runtime.
CMD streamlit run app/app.py \
    --server.port=${PORT} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --server.enableCORS=false
