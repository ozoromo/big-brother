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
    libjpeg-dev \
    liblapack-dev \
    libswscale-dev \
    pkg-config \
    python3-dev \
    python3-numpy \
    software-properties-common \
    zip \
    && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Install HDF5 (for Tensorflow)
RUN apt-get update && apt-get install -y libhdf5-dev

# Install dlib
RUN mkdir -p ~/dlib && \
    git clone https://github.com/davisking/dlib.git ~/dlib/ && \
    cd ~/dlib/ && \
    python3 setup.py install 

# Upgrade pip and install Python packages from requirements.txt
WORKDIR /usr/big-brother
RUN python -m pip install --upgrade pip && \
    python -m pip install -U wheel cmake
COPY requirements.txt /usr/big-brother/


# Install TensorFlow
RUN python -m pip install tensorflow

# Install TensorFlow Addons from source
RUN apt-get update && apt-get install -y \
    python3-pip \
    && pip3 install --upgrade pip setuptools

# Clone TensorFlow Addons repository from GitHub
RUN git clone --depth 1 https://github.com/tensorflow/addons.git /tmp/tensorflow-addons

# Build and install TensorFlow Addons
RUN cd /tmp/tensorflow-addons && python3 ./configure.py && python3 setup.py install

# Clean up
RUN rm -rf /tmp/tensorflow-addons

# Install other Python dependencies
RUN python -m pip install -r requirements.txt

# Copy the application code to the container
COPY . /usr/big-brother

# Set work directory and port
ENV LOCALDEBUG=0
ENV FLASK_DEBUG=0
EXPOSE 3000

# Command to run the Flask app
CMD ["python", "/usr/big-brother/src/web_application/run.py"]
