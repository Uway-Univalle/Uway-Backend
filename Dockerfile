FROM python:3.11.4-slim-bullseye

# Install necessary tools to compile and install GDAL
RUN apt-get update && \
    apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    libgdal-dev \
    python3-gdal \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .

RUN pip install -r requirements.txt
COPY . /app/