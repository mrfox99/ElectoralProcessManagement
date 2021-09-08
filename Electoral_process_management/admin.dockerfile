FROM python:3

RUN mkdir -p /opt/src/admin_service
WORKDIR /opt/src/admin_service

COPY requirements.txt ./requirements.txt
RUN pip install -r ./requirements.txt

COPY run_admin.py ./run_admin.py
COPY configuration.py ./configuration.py
COPY validation.py ./validation.py
COPY models.py ./models.py
COPY Admin ./Admin

ENV TZ=Europe/Belgrade

ENTRYPOINT ["python", "./run_admin.py"]
