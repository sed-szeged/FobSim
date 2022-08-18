FROM python:3.9

ADD main.py .

RUN apt update
RUN apt install -y python3-pip
RUN apt-get install -y python3-pip
RUN apt install python3-rsa

COPY . .

CMD ["python3", "./main.py"]
