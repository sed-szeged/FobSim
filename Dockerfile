FROM python:3.9

ADD main.py .

RUN apt update
RUN apt install -y python3-pip
RUN python3 -m pip install --upgrade pip
RUN apt-get install -y python3-pip
RUN pip install rsa
RUN apt install -y python3-rsa
RUN pip install cryptography

COPY . .

CMD ["python3", "./main.py"]
