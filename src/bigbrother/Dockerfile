FROM slcnx/python310-alpine

WORKDIR /bigbrother

COPY . /bigbrother

#RUN pip3 install -r requirements.txt

RUN pip install --upgrade pip
RUN python -m pip install flask  
RUN python -m pip install flask_socketio   
RUN python -m pip install flask_login  
RUN python -m pip install pillow
RUN python -m pip install CMake    
RUN python -m pip install numpy
RUN python -m pip install pymongo     
RUN python -m pip install pytz  
#RUN python -m pip install opencv-python opencv-contrib-python    
RUN python -m pip install onnx 
RUN python -m pip install onnxruntime
RUN python -m pip install onnx_tf    
RUN python -m pip install tensorflow
RUN python -m pip install tensorflow_probability
RUN python -m pip install imutils  
RUN python -m pip install flask_wtf 
RUN python -m pip install matplotlib
RUN python -m pip install wtforms==2.3.3
RUN python -m pip install dlib-binary
RUN python -m pip install imageio  

CMD python -m flask --app .\bigbrother\app\__init__.py --debug run