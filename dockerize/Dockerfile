FROM python:3.9-slim

EXPOSE 5000

RUN apt update && \
    apt-get install -y git npm libpq-dev && \
    rm -rf /var/lib/apt/lists/*


# RUN localedef -c -f UTF-8 -i en_US en_US.UTF-
# Supposedly helps with pip time-outs.
ENV PIP_DEFAULT_TIMEOUT=100

# setuptools pinned for 2to3 compatibility (for e.g. fs==0.5.4)
RUN python3 -m pip install --upgrade pip setuptools==57.5.0 wheel email_validator && \
     python3 --version && \
     pip3 --version

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"
ENV B2SHARE_WEBUI_MATOMO_URL=''
ENV B2SHARE_WEBUI_MATOMO_SITEID=''

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
    cp dist/license-selector.* /eudat/b2share/webui/app/vendors/ && \
    rm -rf /eudat/public-license-selector

WORKDIR /eudat/b2share
ADD setup.py setup.py
ADD b2share/version.py b2share/version.py
ADD requirements.txt requirements.txt

RUN pip3 install -r requirements.txt && \
    pip3 install -e .

WORKDIR /eudat/b2share/demo
ADD demo/setup.py setup.py
RUN pip3 install -e . && \
    apt-get -y remove libpq-dev && \
    apt-get clean

COPY dockerize/b2share.sh /eudat/
COPY dockerize/supervisord.conf /etc/

#
# Copy the rest of B2Share files
#

WORKDIR /eudat/b2share
ADD webui webui
WORKDIR /eudat/b2share/webui
RUN npm install --unsafe-perm
RUN node_modules/webpack/bin/webpack.js -p

RUN rm -rf ./node_modules

WORKDIR /eudat
ADD . b2share

WORKDIR /eudat/b2share

CMD ["/eudat/b2share.sh"]