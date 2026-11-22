FROM python:3.12-slim

RUN useradd --create-home --uid 10001 app \
 && mkdir -p /app /data \
 && chown app:app /app /data

WORKDIR /app
COPY --chown=app:app server.py ./
COPY --chown=app:app static ./static
RUN chmod -R u+rwX,go+rX /app

USER app
ENV PORT=8080 DATA_DIR=/data
EXPOSE 8080
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8080/api/health')" || exit 1
CMD ["python", "/app/server.py"]
