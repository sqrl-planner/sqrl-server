FROM python:3.9.0-slim-buster as APP

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends build-essential curl libpq-dev \
  && apt-get install -y git \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && chown python:python -R /app

RUN chmod -R 777 /usr/local/src

USER python

# Install poetry
RUN pip3 install --user --no-cache-dir "poetry>=1.0.0"
ENV PATH="/home/python/.local/bin:${PATH}"

# Copy pyproject.toml and poetry.lock
COPY --chown=python:python pyproject.toml poetry.lock ./

# Install dependencies only
RUN poetry install --no-interaction --no-ansi --no-root --only main

ARG FLASK_DEBUG="false"
ENV FLASK_DEBUG="${FLASK_DEBUG}" \
    FLASK_APP="sqrl.app" \
    FLASK_SKIP_DOTENV="true" \
    PYTHONUNBUFFERED="true" \
    PYTHONPATH="." \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

COPY --chown=python:python . .

RUN if [ "${FLASK_DEBUG}" = "false" ]; then \
  ln -s /public /app/public && rm -rf /app/public; fi

EXPOSE 8000

# Install project
RUN poetry install --no-interaction --no-ansi --only main

# Use poetry to start a gunicorn server
CMD ["poetry", "run",\
     "gunicorn", "-c", "python:config.gunicorn", "sqrl.app:create_app()"]
