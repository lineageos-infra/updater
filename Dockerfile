FROM golang:1.23.1-alpine as overmind
RUN GO111MODULE=on go install github.com/DarthSim/overmind/v2@latest

FROM python:3.14-alpine
COPY --from=overmind /go/bin/overmind /usr/local/bin/overmind

RUN apk add --no-cache curl build-base tmux redis
RUN curl -L https://github.com/oliver006/redis_exporter/releases/download/v1.31.4/redis_exporter-v1.31.4.linux-amd64.tar.gz -o exporter.tgz \
  && tar xvzf exporter.tgz \
  && cp redis_exporter-*/redis_exporter /usr/local/bin/redis_exporter \
  && rm -rf *exporter*

ARG VERSION=dev
ENV VERSION=$VERSION

COPY . /app
WORKDIR /app

ENV GERRIT_URL "https://review.lineageos.org"
ENV CACHE_DEFAULT_TIMEOUT "3600"
ENV CACHE_TYPE "simple"
ENV CACHE_REDIS_HOST "redis"
ENV CACHE_REDIS_DB 4
ENV WIKI_INSTALL_URL "https://wiki.lineageos.org/devices/{device}/install"
ENV WIKI_INFO_URL "https://wiki.lineageos.org/devices/{device}"
ENV UPSTREAM_URL ""
ENV DOWNLOAD_BASE_URL "https://mirrorbits.lineageos.org"
ENV FLASK_APP "app.py"

RUN pip install -r requirements.txt

EXPOSE 8080

ENV prometheus_multiproc_dir=/app/metrics/

CMD /usr/local/bin/overmind start
