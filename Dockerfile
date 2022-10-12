FROM python:3.9-alpine

RUN apk update && \
    apk upgrade && \
    apk add bash

RUN addgroup -g 1000 app && \
    adduser -D -u 1000 -G app app -h /app
USER app

COPY requirements.txt /app
RUN python3 -m venv /app/venv && \
    /app/venv/bin/pip --disable-pip-version-check install --upgrade --no-cache-dir pip wheel && \
    /app/venv/bin/pip install --no-cache-dir --requirement /app/requirements.txt

COPY --chown=app:app slack-reddit /app/
COPY --chown=app:app src/ /app/src/

STOPSIGNAL SIGINT
WORKDIR /app
CMD ["/bin/bash"]
