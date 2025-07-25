FROM python:3.9-slim as backend
WORKDIR /app
COPY Ingestion_pipeline/ Ingestion_pipeline/
COPY RAG/ RAG/
RUN pip install --upgrade pip && \
    pip install -r Ingestion_pipeline/requirements.txt && \
    pip install -r RAG/requirements.txt && \
    pip install supervisor flask
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

FROM node:18 as frontend-build
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN cd frontend && npm install
COPY frontend/ ./frontend/
RUN cd frontend && npm run build

FROM python:3.9-slim
WORKDIR /app
COPY --from=backend /app /app
COPY --from=frontend-build /app/frontend/build /app/frontend/build
RUN pip install --upgrade pip && \
    pip install -r Ingestion_pipeline/requirements.txt && \
    pip install -r RAG/requirements.txt && \
    pip install supervisor flask
COPY serve_frontend.py /app/serve_frontend.py
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
EXPOSE 3000
CMD ["/usr/local/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"] 