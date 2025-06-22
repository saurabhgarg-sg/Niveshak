# app/Dockerfile

FROM ghcr.io/ukewea/python-talib:latest

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/saurabhgarg-sg/Niveshak.git .

RUN /venv/bin/pip3 install -r requirements.txt

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["/venv/bin/streamlit", "run", "Niveshak/src/niveshak.py", "--server.port=8501", "--server.address=0.0.0.0"]
