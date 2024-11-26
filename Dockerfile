# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

WORKDIR /MQC

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

RUN apt-get update && apt-get install -y vim tmux

RUN cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && echo 'Asia/Shanghai' >/etc/timezone

COPY . .

CMD [ "python3", "MainLoop.py"]