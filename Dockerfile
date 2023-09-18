FROM ubuntu:22.04

MAINTAINER FCG "melifernandez@ciencias.unam.mx"

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev && \
    apt install -y vim tmux netcat

WORKDIR /app

COPY . /app