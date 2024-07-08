FROM python:3.9

ENV PYTHONUNBUFFERED 1

EXPOSE 8000
WORKDIR /

RUN apt-get update && \
    apt-get install -y --no-install-recommends netcat-openbsd && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

#COPY poetry.lock pyproject.toml ./
COPY pyproject.toml ./
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-dev && \
    poetry run pip install -U pip setuptools && \
    poetry run pip install --upgrade git+https://github.com/vmware/vsphere-automation-sdk-python.git

COPY ./app /app

CMD uvicorn app.main:app --host=0.0.0.0 --port 8000
