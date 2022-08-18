FROM python:3.9

ADD main.py .

RUN sudo apt update
RUN sudo apt install python3-pip
RUN sudo apt install python3-rsa

CMD ["python3", "./main.py"]
