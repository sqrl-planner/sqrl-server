FROM python:3.9.0-slim-buster AS app

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
  && apt-get install -y git \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && chown python:python -R /app

USER python

COPY --chown=python:python requirements*.txt ./
COPY --chown=python:python bin/ ./bin

RUN chmod 0755 bin/* && bin/pip3-install

ARG FLASK_ENV="production"
ENV FLASK_ENV="${FLASK_ENV}" \
    FLASK_APP="sqrl.app" \
    FLASK_SKIP_DOTENV="true" \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

COPY --chown=python:python . .

RUN if [ "${FLASK_ENV}" != "development" ]; then \
  ln -s /public /app/public && rm -rf /app/public; fi

RUN pip3 install --user --no-cache-dir .  # run setup.py

EXPOSE 8000

RUN flask sync -y

CMD ["gunicorn", "-c", "python:config.gunicorn", "sqrl.app:create_app()"]
