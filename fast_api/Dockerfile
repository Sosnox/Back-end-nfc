FROM python:3.8-slim

# Set work directory
WORKDIR /app

# Copy the requirements file
COPY ./requirements.txt /app/requirements.txt

# Ensure that we have the latest information about the Debian repositories and bypass any key expiration checks temporarily
RUN apt-get update -o Acquire::Check-Valid-Until=false \
    && apt-get install -y gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy the rest of the application
COPY . /app/

# Optional: Verify that gcc is installed (This step can be removed, it's just for debugging purposes)
RUN gcc --version
