FROM python:3.12.5-slim-bullseye

RUN pip3 install gunicorn

RUN mkdir /opt/frx-challenges

COPY . /opt/frx-challenges

WORKDIR /opt/frx-challenges

RUN pip3 install -r requirements.txt
