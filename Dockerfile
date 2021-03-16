FROM ubuntu:20.04
#FROM balenalib/rpi-raspbian:latest

ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Europe/Rome
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

ENV LC_CTYPE it_IT.UTF-8
ENV LANG it_IT.UTF-8
ENV PYTHONIOENCODING utf-8

COPY . /app
WORKDIR /app

RUN apt-get update

RUN apt-get install -y language-pack-it
RUN apt-get install -y texlive-latex-base texlive-latex-extra texlive-lang-italian
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
CMD [ "sh", "/app/run.sh" ]
