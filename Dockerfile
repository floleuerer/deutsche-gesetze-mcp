FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get -y install git
RUN git clone https://github.com/bundestag/gesetze.git

COPY mcp/ .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "server.py"]
