# Dockerfile
FROM python:3.11-slim

# set workdir
WORKDIR /app

# copy requirements and app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy application code and assets
COPY . /app

# expose port used by streamlit
EXPOSE 8501

# environment defaults (can be overridden at runtime)
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV PYTHONUNBUFFERED=1

# streamlit config location (optional)
RUN mkdir -p /root/.streamlit
# keep as-is; you can optionally COPY .streamlit/config.toml

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
