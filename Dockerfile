FROM python:3.9.10-slim-bullseye

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg
RUN pip install --upgrade pip

WORKDIR /flaskapp

COPY ./api/requirements.txt .

RUN pip install -r requirements.txt

COPY ./api/src ./api/src

WORKDIR /flaskapp/api/src

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app:app"]
