# original source
# https://github.com/erstrom/docker-opencv


FROM ubuntu:16.04

ENV OPENCV_VERSION 3.2.0

# upgrade/update 
RUN apt-get -y upgrade
RUN apt-get -y update

# Build prerequisites
RUN apt-get -y install build-essential cmake pkg-config git libgtk-3-dev \
	libatlas-base-dev gfortran python3 python3.5-dev

# Image related packages
RUN apt-get -y install libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev

# ADDED: JPEG support for python pil
RUN apt-get -y install libfreetype6 libfreetype6-dev zlib1g-dev

# Video related packages
RUN apt-get -y install libavcodec-dev libavformat-dev libswscale-dev \
	libv4l-dev libxvidcore-dev libx264-dev

# Python packages
RUN apt-get -y install python3-pip
RUN pip3 install numpy pillow

# build 
RUN mkdir -p /opencv/build
WORKDIR /opencv/build
ADD build_opencv.sh /opencv/build/build_opencv.sh
RUN chmod u+x /opencv/build/build_opencv.sh 
RUN OPENCV_VERSION=$OPENCV_VERSION /opencv/build/build_opencv.sh

