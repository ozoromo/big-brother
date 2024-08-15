# Use the official TensorFlow Docker image as the base image
FROM tensorflow/tensorflow:2.12.0-gpu

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variable for CUDA
ENV LD_LIBRARY_PATH /usr/local/cuda/lib64:$LD_LIBRARY_PATH
ENV CUDA_HOME /usr/local/cuda

# Set the default command to run your script
CMD ["python", "benchmark.py"]
