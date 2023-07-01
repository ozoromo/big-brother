FROM ubuntu:latest

WORKDIR /bigbrother

COPY . /bigbrother

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip

RUN pip3 install -r requirements.txt

CMD ["python -m flask --app .\app\__init__.py --debug run"]