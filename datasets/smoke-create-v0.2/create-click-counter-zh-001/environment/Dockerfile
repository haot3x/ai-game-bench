FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

# Keep the Python package and bundled Chromium revision in sync. Everything
# needed by verification is installed at build time, never during a trial.
RUN pip install --no-cache-dir playwright==1.62.0 pytest==8.4.2

WORKDIR /workspace
