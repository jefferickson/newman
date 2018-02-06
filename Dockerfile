FROM debian:jessie

RUN apt-get update
RUN apt-get install -y curl
RUN curl -sL https://deb.nodesource.com/setup_7.x | apt-get install -y nodejs
RUN apt-get install -y npm
RUN npm install -g n
RUN n v9.5.0
RUN apt-get install -y python-dev
RUN apt-get install -y python-setuptools
RUN easy_install pip
