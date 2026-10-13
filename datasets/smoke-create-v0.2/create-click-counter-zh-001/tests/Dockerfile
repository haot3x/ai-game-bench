FROM mcr.microsoft.com/playwright/python:v1.62.0-noble

RUN pip install --no-cache-dir playwright==1.62.0 pytest==8.4.2

# Harbor separate-verifier mode builds this directory as its own context.
# The agent never receives this image's /tests or its Python installation.
COPY . /tests
WORKDIR /workspace
