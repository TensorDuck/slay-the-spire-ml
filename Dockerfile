FROM python:3.8-slim
EXPOSE 8080
WORKDIR /app
COPY requirements.txt ./requirements.txt
RUN pip3 install -r requirements.txt
COPY slayer slayer
COPY app.py app.py
COPY scripts scripts
ENV PYTHONPATH=/app:$PYTHONPATH

ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080"]
