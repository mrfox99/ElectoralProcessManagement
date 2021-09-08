FROM python:3

RUN mkdir -p /opt/src/authentication_service
WORKDIR /opt/src/authentication_service

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY run.py ./run.py
COPY configuration.py ./configuration.py
COPY Authentication ./Authentication

ENV TZ=Europe/Belgrade

ENTRYPOINT ["python", "./run.py"]
