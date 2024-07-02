FROM python:3.10-slim-bullseye

ENV PIP_ROOT_USER_ACTION=ignore

# System packages needed for runtime
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    tesseract-ocr \
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
    libhdf5-dev\
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

RUN mkdir -p ~/dlib && \
    git clone https://github.com/davisking/dlib.git ~/dlib/ && \
    cd ~/dlib/ && \
    python3 setup.py install 

# Upgrade pip and install Python packages from requirements.txt
WORKDIR /usr/big-brother
COPY requirements.txt /usr/big-brother/
RUN python -m pip install --upgrade pip && \
    python -m pip install -U wheel cmake && \
    python -m pip install -r requirements.txt


# Copy the application code to the container
COPY . /usr/big-brother

# Set work directory and port
ENV LOCALDEBUG=0
ENV FLASK_DEBUG=0
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "/usr/big-brother/src/web_application/run.py"]
