FROM python:3.12-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /usr/src/app

# System deps: ffmpeg, aria2c, mediainfo, libmagic, qbittorrent-nox,
# build tools for cryptography/lxml/aiohttp, fonts, cleanup tooling.
RUN apt-get update && apt-get install -y --no-install-recommends \
        bash \
        ca-certificates \
        curl \
        wget \
        git \
        gnupg \
        aria2 \
        qbittorrent-nox \
        ffmpeg \
        libmediainfo-dev \
        mediainfo \
        libmagic-dev \
        libpq-dev \
        libxml2-dev \
        libxslt1-dev \
        libffi-dev \
        libssl-dev \
        libjpeg-dev \
        zlib1g-dev \
        libsqlite3-dev \
        fonts-dejavu-core \
        fontconfig \
        unzip \
        xz-utils \
        build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && fc-cache -f

# Setuptools ko pehle upgrade karo (PEP 517 wheels ke liye)
RUN pip3 install --upgrade setuptools pip wheel

# PyPI se na-milne wale pip options ko ensure karna
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt \
    && pip3 install --no-cache-dir "setuptools<81"

# Bot code copy
COPY . .
RUN chmod +x start.sh

CMD ["bash", "start.sh"]
