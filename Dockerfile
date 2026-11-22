FROM python:3.15-slim
WORKDIR /app
COPY server.py .
COPY site ./site
COPY scripts/manage_leads.py ./scripts/manage_leads.py
RUN mkdir -p /app/data && useradd --system --uid 10001 --home-dir /app website && chown -R website:website /app/data
USER website
EXPOSE 8097
ENV MMS_HOST=0.0.0.0 MMS_PORT=8097 MMS_DATABASE=/app/data/leads.sqlite3
CMD ["python","server.py"]
