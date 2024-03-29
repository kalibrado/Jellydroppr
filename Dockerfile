FROM python:3.10.8
RUN apt update && apt install -y ffmpeg

ADD modules /modules
ADD config /config
ADD main.py /main.py

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD python3 /main.py