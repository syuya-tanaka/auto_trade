FROM python:3.10.12-slim-bullseye AS base
ENV PYTHONUNBUFFERED 1
WORKDIR /src
COPY ./fx_trading/requirements.txt /src
COPY ./fx_trading /src
RUN apt-get update && apt-get -y upgrade && \
    apt-get install -y \
        libpq-dev && \
    apt-get clean && \
    pip install --upgrade pip && pip install -r requirements.txt

FROM base AS dev
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/lib/python3.10/site-packages \
    /usr/local/lib/python3.10/site-packages

FROM base AS prod
COPY --from=base /usr/local/bin /usr/local/bin
COPY --from=base /usr/local/lib/python3.10/site-packages \
    /usr/local/lib/python3.10/site-packages

