FROM python:3.10.8
RUN apt update && apt install -y ffmpeg

ADD modules /Jellydroppr/modules
ADD config /Jellydroppr/config
ADD main.py /Jellydroppr/main.py

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

CMD python3 /Jellydroppr/main.py
