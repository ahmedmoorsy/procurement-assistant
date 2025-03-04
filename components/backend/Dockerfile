FROM python:3.10-slim AS builder


RUN pip install poetry
RUN mkdir -p /app
COPY src/ /app/src
COPY pyproject.toml /app

WORKDIR /app
RUN poetry config virtualenvs.in-project true
RUN poetry install && \
rm -rf /root/.cache

FROM python:3.10-slim AS base
RUN addgroup --system nonroot \
    && adduser --system nonroot --ingroup nonroot

COPY --from=builder /app /app
RUN chown -R nonroot:nonroot /app

USER nonroot
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8000
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "-w", "1", "-b", "0.0.0.0:8000", "--timeout", "300", "--chdir", "src", "app:app"]
