# syntax=docker/dockerfile:1

FROM python:3.9-slim-buster

# Get dependencies
RUN apt-get -y update
RUN apt-get -y install git

# Setup environment
WORKDIR /sqrl-server

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .
RUN pip install -e .

CMD [ "python3", "-m", "flask", "run", "--host=0.0.0.0"]