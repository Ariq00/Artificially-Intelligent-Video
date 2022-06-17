FROM python:3.9.10-slim-bullseye

RUN apt-get update
RUN apt-get -y upgrade
RUN apt-get install --no-install-recommends -y ffmpeg libavcodec-extra
RUN pip install --upgrade pip

WORKDIR /flaskapp

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY ./src ./src

WORKDIR /flaskapp/src

ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8000", "app:app", "--timeout", "120"]