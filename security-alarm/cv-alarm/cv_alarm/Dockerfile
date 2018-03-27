# Use a python3 base image
FROM python:3.6-stretch

# update
RUN apt-get update -y

# Get requests
RUN pip install requests

# Download images
WORKDIR /app/testing
ADD get_test_data.py .
RUN mkdir -p /data/images
RUN python3 get_test_data.py

# add the local file
#WORKDIR /app
#ADD helloworld.py .
#ADD get_test_data.py .

# run the app when container launches. There can only be one cmd
# CMD ["python3", "helloworld.py"]
#CMD ["python3", "get_test_data.py"]

CMD echo `ls /data/images`
