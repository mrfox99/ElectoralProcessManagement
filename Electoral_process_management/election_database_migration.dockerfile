FROM python:3

RUN mkdir -p /opt/src/authentication_database_migration
WORKDIR /opt/src/authentication_database_migration

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY configuration.py ./configuration.py
COPY models.py ./models.py
COPY migration.py ./migration.py

ENV INITIALIZATION=True
ENV TZ=Europe/Belgrade

ENTRYPOINT ["python", "./migration.py"]