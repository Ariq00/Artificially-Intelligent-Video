FROM python:3.9.10-slim-bullseye

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install --upgrade pip

WORKDIR /flask_app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

WORKDIR /flask_app/src

#CMD ["python", "app.py"]
