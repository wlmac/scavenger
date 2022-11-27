FROM alpine:3.17

EXPOSE 3031 9091
# 3031 is uwsgi socket
# 9091 is uwsgi stats

RUN apk add --no-cache \
    uwsgi-python3 \
    python3 \
    py3-pip

RUN pip install virtualenv
RUN python -m venv /venv
RUN /venv/bin/pip install pipenv
COPY ./scavenger2022 /app
WORKDIR /app
RUN rm -f /app/scavenger2022/local_settings.py
RUN /venv/bin/pipenv sync
COPY ./config/uwsgi.conf /opt/uwsgi.conf
CMD uwsgi --ini /opt/uwsgi.conf
