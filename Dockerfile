# Dockerfile for local testing
# build with docker build -t smplchat .
# run with docker run -it --rm smplchat
# debug mode with docker run -it --rm -e DEBUG=1 smplchat
FROM python:3.12-slim

WORKDIR /app

COPY . /app

RUN pip install .

CMD ["smplchat"]
