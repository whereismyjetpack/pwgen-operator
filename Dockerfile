FROM python:3.9.7-slim-buster

WORKDIR /pwgen

RUN useradd -m pwgen

RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY --chown=pwgen pyproject.toml poetry.lock /pwgen/
RUN poetry install
USER pwgen
COPY --chown=pwgen . /pwgen

CMD ["kopf", "run", "pwgen.py"]
