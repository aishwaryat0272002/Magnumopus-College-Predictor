FROM python:3.12.3-slim as app
WORKDIR /collegepredictor
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
RUN export FLASK_ENV=development
RUN export FLASK_APP=run.py
