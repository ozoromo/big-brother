FROM python:3.10-slim-bullseye

WORKDIR /bigbrother

COPY . /bigbrother

RUN python -m pip install --upgrade pip

RUN python -m pip install cmake

RUN python -m pip install opencv-contrib-python

RUN python -m pip install pymongo

#Flask Dependencies
RUN python -m pip install flask
RUN python -m pip install flask_wtf
RUN python -m pip install werkzeug
RUN python -m pip install wtforms==2.3.3
RUN python -m pip install Flask-SocketIO
RUN python -m pip install flask-login
RUN python -m pip install imageio

#opencv
#RUN python -m pip install opencv-contrib-python-headless
RUN python -m pip install onnx
RUN python -m pip install onnx_tf
RUN python -m pip install onnxruntime
RUN python -m pip install tensorflow
RUN python -m pip install imutils
RUN python -m pip install dlib-binary

#Math/Plotting
RUN python -m pip install numpy
RUN python -m pip install pandas
RUN python -m pip install matplotlib
RUN python -m pip install Pillow

#Database
#pickle
RUN python -m pip install uuid

#RUN python -m pip install open-faces

EXPOSE 8000

CMD python -m flask --app ./app/__init__.py --debug run