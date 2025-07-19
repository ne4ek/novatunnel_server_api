FROM python:3.11.13

WORKDIR /app

ENV PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION=python

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
