FROM python:3.6.9-alpine


WORKDIR /usr/src/app


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk --no-cache add musl-dev linux-headers g++
RUN apk add postgresql-dev libffi-dev
RUN pip install --upgrade pip
COPY requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

COPY entrypoint.sh /usr/src/app/entrypoint.sh
COPY . /usr/src/app/
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]