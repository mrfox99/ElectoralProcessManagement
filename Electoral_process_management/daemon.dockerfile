FROM python:3

RUN mkdir -p /opt/src/daemon_service
WORKDIR /opt/src/daemon_service

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY run_daemon.py ./run_daemon.py
COPY configuration.py ./configuration.py
COPY validation.py ./validation.py
COPY models.py ./models.py
COPY Daemon ./Daemon

ENV TZ=Europe/Belgrade

ENTRYPOINT ["python", "./run_daemon.py"]
