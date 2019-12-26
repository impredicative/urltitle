FROM python:3.7-slim as build
WORKDIR /app
COPY ./requirements/install.in ./requirements/install.in
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir -Ur ./requirements/install.in
COPY urltitle urltitle
RUN useradd --user-group --system --create-home --no-log-init app
USER app

FROM build as test
WORKDIR /app
USER root
COPY pylintrc pyproject.toml setup.cfg ./
COPY ./requirements/dev.in ./requirements/dev.in
COPY tests tests
COPY scripts scripts
RUN \
    pip install --no-cache-dir -Ur ./requirements/dev.in && \
    ./scripts/test.sh

#FROM build as publish
#WORKDIR /app
#USER root
#COPY setup.py ./
#COPY ./requirements/publish.in ./requirements/publish.in
#RUN pip install --no-cache-dir -Ur ./requirements/publish.in

FROM build
