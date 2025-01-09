FROM python:3.10-slim AS builder

RUN pip install poetry
RUN mkdir -p /app
COPY src/ /app/src
COPY data/ /app/data
COPY pyproject.toml /app

WORKDIR /app
RUN poetry config virtualenvs.in-project true
RUN poetry install

FROM python:3.10-slim AS base
RUN addgroup --system nonroot \
    && adduser --system nonroot --ingroup nonroot

COPY --from=builder /app /app
RUN chown -R nonroot:nonroot /app

USER nonroot
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
ENV HF_HOME="/app/cache/huggingface"

CMD ["python", "src/main.py"]
