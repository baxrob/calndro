FROM python:3-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /code
#COPY requirements/* /code/requirements/
#RUN set -ex && pip install --upgrade pip && pip install -r requirements/local.txt

COPY . /code/

RUN set -ex && pip install --upgrade pip \
    && pip install -r requirements/local.txt \
    && ./scripts/reset.sh
RUN set -ex && ls -lhtrA \
    && ./manage.py check && whoami \
    && python --version && cat /etc/os-release

EXPOSE 8000
CMD ["./manage.py", "runserver", "0.0.0.0:8000"]

