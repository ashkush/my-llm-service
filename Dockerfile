FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- New Step: Pre-download the model ---
# This ensures the 1GB+ files are part of the image layers
RUN python -c "from transformers import AutoModelForCausalLM, AutoTokenizer; \
    m='Qwen/Qwen2.5-0.5B-Instruct'; \
    AutoModelForCausalLM.from_pretrained(m); \
    AutoTokenizer.from_pretrained(m)"

FROM python:3.11-slim AS runner
WORKDIR /app
COPY --from=builder /root/.local /root/.local
# Copy the downloaded Hugging Face cache from the builder
COPY --from=builder /root/.cache/huggingface /root/.cache/huggingface

COPY ./app ./app
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]