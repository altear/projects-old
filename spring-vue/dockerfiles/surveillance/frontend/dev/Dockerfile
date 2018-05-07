FROM ubuntu:16.04

RUN apt-get -y update
RUN apt-get -y install curl

# install nodejs
# https://nodejs.org/en/
RUN curl -sL https://deb.nodesource.com/setup_9.x | bash -
RUN apt-get -y update
RUN apt-get install -y nodejs

# make a dev directory for mounting when we run this image, we should mount the
# local dev code, so that our changes will be uploaded
RUN mkdir frontend-source
WORKDIR frontend-source
RUN npm install

# run a dev setup on port 8080
ENTRYPOINT npm run dev
