FROM python:3.9.10-slim-bullseye

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip install --upgrade pip

WORKDIR /AIVideo-app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./api ./api

WORKDIR /AIVideo-app/api/src

EXPOSE 5000

CMD ["python", "app.py"]
