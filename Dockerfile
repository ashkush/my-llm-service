# --- Stage 1: Builder ---
# We use a full python image to have the compilers needed for some ML libs
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build tools for potential C-extensions in ML libraries
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements to leverage Docker cache
COPY requirements.txt .

# Install dependencies into a specific directory
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: Runner ---
# Use a slim image for the final production environment
FROM python:3.11-slim AS runner

WORKDIR /app

# Copy only the installed python packages from the builder stage
COPY --from=builder /root/.local /root/.local
COPY ./app ./app

# Ensure the local bin is in the PATH so we can run uvicorn
ENV PATH=/root/.local/bin:$PATH
# Prevent Python from writing .pyc files (keeps container clean)
ENV PYTHONDONTWRITEBYTECODE=1
# Ensure logs are sent straight to the terminal (useful for Azure Logs)
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Use 2 workers to handle concurrent requests without overwhelming the CPU
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]