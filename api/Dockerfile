FROM python:3.10-alpine

WORKDIR /usr/src/app

COPY requirements.txt requirements.txt
RUN apk add --no-cache postgresql-libs && \
    apk add --no-cache --virtual .build-deps gcc musl-dev postgresql-dev && \
    pip install -r requirements.txt && \
    apk --purge del .build-deps

COPY data data
COPY adventure_api adventure_api

CMD ["python", "adventure_api"]
