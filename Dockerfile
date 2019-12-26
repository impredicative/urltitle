FROM python:3.7-slim as build
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -Ur ./requirements.txt
COPY mypackage mypackage
RUN useradd --user-group --system --create-home --no-log-init app
USER app

FROM build as test
WORKDIR /app
USER root
COPY pylintrc pyproject.toml requirements-dev.in setup.cfg ./
COPY tests tests
COPY scripts/test.sh ./scripts/test.sh
# Note: `gcc` compiles `regex` which is required by `black`.
RUN \
    apt-get update && apt-get -y install gcc && \
    pip install --no-cache-dir -Ur requirements-dev.in && \
    ./scripts/test.sh

FROM build
