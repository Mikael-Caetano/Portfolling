# Base Image
FROM python:3.8
#set working directory
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
COPY ./portfoling/ /app/
COPY ./portfolio/ /app/
COPY manage.py /app/


# set default environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV DEBUG 0
ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-setuptools \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# install environment dependencies
RUN pip3 install --upgrade pip 

# install dependencies
RUN pip install -r requirements.txt