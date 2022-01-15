# syntax=docker/dockerfile:1
#FROM python:3
FROM python:3-alpine
#FROM python:3.10.1-alpine3.15
#FROM python:3.9.9-alpine3.15
RUN apk add --no-cache  gcc libffi-dev musl-dev
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt
COPY . /code/
ENV DATABASE_URL=sqlite:////code/db.sqlite3
RUN set -ex && ls -lhtrA && ./manage.py check && whoami && ./reset.sh \
    && python --version && cat /etc/os-release
EXPOSE 8000
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
