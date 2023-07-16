FROM python:3.10-slim-bullseye

ENV PIP_ROOT_USER_ACTION=ignore

# from: https://github.com/ageitgey/face_recognition/blob/master/Dockerfile
# Used to build dlib
RUN apt-get -y update
RUN apt-get install -y --fix-missing \
    build-essential \
    cmake \
    gfortran \
    git \
    wget \
    curl \
    graphicsmagick \
    libgraphicsmagick1-dev \
    libatlas-base-dev \
    libavcodec-dev \
    libavformat-dev \
    libgtk2.0-dev \
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /tmp/* /var/tmp/*
RUN cd ~ && \
    mkdir -p dlib && \
    git clone -b 'v19.9' --single-branch https://github.com/davisking/dlib.git dlib/ && \
    cd  dlib/ && \
    python3 setup.py install --yes USE_AVX_INSTRUCTIONS


RUN mkdir -p /usr/big-brother
WORKDIR /usr/big-brother

# installations
RUN python -m pip install --upgrade pip
RUN python -m pip install -U wheel cmake
COPY requirements.txt /usr/big-brother/requirements.txt
#RUN python -m pip install --no-cache-dir -r requirements.txt
RUN python -m pip install -r requirements.txt

COPY . /usr/big-brother/src

# Flask app config and starting
ENV LOCALDEBUG=0
ENV FLASK_DEBUG=0
EXPOSE 5000
CMD ["python", "./src/bigbrother/app/__init__.py"]
