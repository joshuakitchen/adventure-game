FROM python:3.8-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY data data
COPY adventure_api adventure_api
COPY admin.py admin.py
COPY main.py main.py

CMD ["python", "main.py"]
