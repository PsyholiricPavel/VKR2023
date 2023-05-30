FROM python:3.8

WORKDIR /app

COPY . .

RUN pip3 install -r requirements.txt
RUN apt-get update && apt-get install -y libgl1-mesa-glx