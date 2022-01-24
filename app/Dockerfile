FROM python:3.8-slim
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update
RUN apt-get install python3-dev default-libmysqlclient-dev gcc -y
RUN apt-get install graphviz -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt