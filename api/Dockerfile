FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY data data
COPY adventure_api adventure_api
COPY main.py main.py

CMD ["python", "main.py"]
