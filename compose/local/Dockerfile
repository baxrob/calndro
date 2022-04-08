FROM python:3-alpine

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

WORKDIR /code
COPY requirements/* /code/requirements/
RUN set -ex && pip install --upgrade pip && pip install -r requirements/local.txt

#COPY . /code/
COPY . .

#
RUN set -ex && ls -lhtrA && find . \
#    && ./manage.py check && whoami \
#    && env \
    && python --version && cat /etc/os-release

#RUN set -ex && pip install --upgrade pip \
#    && pip install -r requirements/local.txt \
#    && ./scripts/reset.sh
RUN set -ex && env && cat compose/local/dj.env
#RUN ./manage.py migrate


EXPOSE 8000
#CMD ["./manage.py", "runserver", "0.0.0.0:8000"]
CMD ["sh", "-c", "scripts/reset.sh && ./manage.py runserver 0.0.0.0:8000"]
#CMD scripts/reset.sh && ./manage.py runserver 0.0.0.0:8000

