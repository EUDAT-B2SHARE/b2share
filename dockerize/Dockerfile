#
# Building the webui
#
FROM node:12.22.12-buster-slim AS web

LABEL maintainer Joni Tahvanainen <joni.tahvanainen@csc.fi>

RUN apt update && \
    apt install -y git

WORKDIR /eudat/b2share
COPY webui webui

WORKDIR /eudat/b2share/webui
RUN npm install --unsafe-perm
RUN node_modules/webpack/bin/webpack.js -p

# Install public-license-selector

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git && \
    apt-get -y remove git
WORKDIR /eudat/public-license-selector
RUN npm install && \
    node --version && \
    npm --version && \
    mv webpack.config.js webpack.config.js.0 && \
    echo "require('es6-promise').polyfill();" > webpack.config.js && \
    cat webpack.config.js.0 >> webpack.config.js && \
    npm install es6-promise && \
    npm run build && \
    node_modules/webpack/bin/webpack.js -p && \
    mkdir -p /eudat/b2share/webui/app/vendors && \
    cp dist/license-selector.* /eudat/b2share/webui/app/vendors/


#
# Building the b2share
#
FROM python:3.6-slim as builder

ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"
ENV B2SHARE_WEBUI_MATOMO_URL=''
ENV B2SHARE_WEBUI_MATOMO_SITEID=''

EXPOSE 5000
# setuptools pinned for 2to3 compatibility (for e.g. fs==0.5.4)
RUN apt update && \
    apt-get install -y gcc libpq-dev npm git && \
    python3 -m pip install --upgrade pip setuptools==57.5.0 wheel



# Supposedly helps with pip time-outs.
ENV PIP_DEFAULT_TIMEOUT=100

# UWSGI Config

WORKDIR /eudat
ADD dockerize/uwsgi.ini b2share/uwsgi/uwsgi.ini

# Install python module and dependencies

WORKDIR /eudat/b2share
ADD setup.py setup.py
ADD b2share/version.py b2share/version.py
ADD requirements.txt requirements.txt

RUN pip3 wheel . --wheel-dir=./wheels -r requirements.txt

COPY dockerize/b2share.sh /eudat/
COPY dockerize/supervisord.conf /etc/

# Copy the rest of B2Share files & remove webui from this stage.

WORKDIR /eudat
ADD . b2share
RUN rm -rf /eudat/b2share/webui

#
# Compiling everything
#
FROM python:3.6-slim

# Variables needed in order to run b2share
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"
ENV B2SHARE_WEBUI_MATOMO_URL=''
ENV B2SHARE_WEBUI_MATOMO_SITEID=''

COPY --from=builder /eudat /eudat
COPY --from=builder /etc/supervisord.conf /etc/

RUN apt update && \
    apt install -y libpq-dev supervisor

WORKDIR /eudat/b2share

RUN pip install --find-links=./wheels -r requirements.txt && \
  pip install -e . && \
  pip cache purge

RUN pip3 install -e .

WORKDIR /eudat/b2share/demo
ADD demo/setup.py setup.py
RUN pip3 install -e .

WORKDIR /eudat/b2share/webui
COPY --from=web /eudat/b2share/webui/app /eudat/b2share/webui/app

WORKDIR /eudat/b2share

USER root

ARG USERNAME=b2share
ARG USER_UID=1000
ARG USER_GID=$USER_UID

EXPOSE 5000

COPY /dockerize/*.sh /eudat/

RUN groupadd --gid $USER_GID $USERNAME && \
  useradd --uid $USER_UID --gid $USER_GID -m $USERNAME && \
  ln -s /usr/var /usr/local/var && \
  mkdir -p /usr/var/b2share-instance && \
  chown $USER_UID:$USER_GID /eudat/b2share /eudat/b2share/b2share /eudat/b2share/b2share/admin && \
  chown -R $USER_UID:$USER_GID /usr/var

USER $USERNAME

CMD ["/eudat/b2share.sh"]
