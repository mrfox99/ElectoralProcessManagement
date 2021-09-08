FROM python:3

RUN mkdir -p /opt/src/voting_station_service
WORKDIR /opt/src/voting_station_service

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY run_voting_station.py ./run_voting_station.py
COPY configuration.py ./configuration.py
COPY validation.py ./validation.py
COPY models.py ./models.py
COPY Voting_station ./Voting_station

ENV TZ=Europe/Belgrade

ENTRYPOINT ["python", "./run_voting_station.py"]
