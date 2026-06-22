# Dockerfile — packages the retail ETL pipeline into a runnable image.
#
# This is what our CD step builds and publishes. Anyone can then run the whole
# pipeline with a single command, no Python setup needed:
#
#     docker run --rm ghcr.io/navik12/retail-sales-etl-elt-pipeline:latest
#
# (It still needs a database to connect to via env vars — the image just bundles
#  the code and its dependencies so it runs identically anywhere.)

# Start from a small official Python image.
FROM python:3.12-slim

# Where our code will live inside the container.
WORKDIR /app

# Install dependencies first (this layer is cached unless requirements change).
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project in.
COPY . .

# By default, running the container runs the full ETL pipeline.
CMD ["python", "run_etl.py"]
