FROM alpine:3.17

EXPOSE 3031 9091
# 3031 is uwsgi socket
# 9091 is uwsgi stats

ENV LANG=C
RUN adduser -s /bin/nologin -S -D -g "App" app
RUN apk add --no-cache \
    uwsgi-python3 \
    python3 \
    py3-pip

RUN mkdir /venv && chown app /venv
USER app
RUN pip install virtualenv --no-warn-script-location
RUN python -m venv /venv
RUN /venv/bin/pip install pipenv

COPY ./scavenger2022 /app
WORKDIR /app
USER root
RUN touch /etc/app-venv-path && \
    chown app /etc/app-venv-path
RUN rm ./scavenger2022/local_settings.py
USER app
RUN /venv/bin/pipenv install --skip-lock
RUN /venv/bin/pipenv --venv > /etc/app-venv-path
COPY ./docker/local_settings.py /app/scavenger2022
RUN /venv/bin/pipenv run ./manage.py check
USER root
RUN rm ./scavenger2022/local_settings.py
USER app

# uwsgi
COPY ./config/uwsgi.conf /opt/uwsgi.conf
CMD uwsgi --ini /opt/uwsgi.conf --virtualenv $(cat /etc/app-venv-path)
