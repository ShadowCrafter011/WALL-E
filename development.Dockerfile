FROM python:3.12

RUN apt-get update && \
    apt-get install ffmpeg -y --no-install-recommends
