FROM centos:7

LABEL maintainer Petri Laihonen <petri.laihonen@csc.fi>

EXPOSE 5000

RUN \
    # yum -y update && \
    yum -y install https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm && \
    yum -y install wget gcc-c++ make openssl-devel \
                   postgresql-devel mysql-devel supervisor \
                   git libffi-devel python-devel libxml2-devel libxml2 \
                   libxslt-devel zlib-devel libxslt http-parser npm

RUN yum -y install python36 python36-pip python36-devel uwsgi-plugin-python36 uwsgi

# install locale
RUN localedef -c -f UTF-8 -i en_US en_US.UTF-8

# Supposedly helps with pip time-outs.
ENV PIP_DEFAULT_TIMEOUT=100

# setuptools pinned for 2to3 compatibility (for e.g. fs==0.5.4)
RUN python3 -m pip install --upgrade pip setuptools==57.5.0 wheel && \
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

#
# Install public-license-selector
#

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git
WORKDIR /eudat/public-license-selector
RUN npm install

# this next RUN is just a workaround for the old version of node on centos7
# without it, the npm run build fails when compiling less files
RUN node --version && \
    npm --version
RUN mv webpack.config.js webpack.config.js.0
RUN echo "require('es6-promise').polyfill();" > webpack.config.js
RUN cat webpack.config.js.0 >> webpack.config.js
RUN npm install es6-promise

RUN npm run build

RUN node_modules/webpack/bin/webpack.js -p
RUN mkdir -p /eudat/b2share/webui/app/vendors
RUN cp dist/license-selector.* /eudat/b2share/webui/app/vendors/

#
# Install B2Share webui module and dependencies
#

WORKDIR /eudat
ADD ./webui/package.json b2share/webui/package.json
ADD ./webui/copy_files.sh b2share/webui/copy_files.sh

WORKDIR /eudat/b2share/webui
RUN npm install --unsafe-perm

#
# UWSGI Config
#

WORKDIR /eudat
ADD dockerize/uwsgi.ini b2share/uwsgi/uwsgi.ini

#
# Install python module and dependencies
#

WORKDIR /eudat/b2share
ADD setup.py setup.py
ADD b2share/version.py b2share/version.py
ADD requirements.txt requirements.txt

RUN pip3 install -r requirements.txt
RUN pip3 install -e .

WORKDIR /eudat/b2share/demo
ADD demo/setup.py setup.py
RUN pip3 install -e .

COPY dockerize/b2share.sh /eudat/
COPY dockerize/supervisord.conf /etc/

#
# Copy the rest of B2Share files
#

WORKDIR /eudat/b2share
ADD webui webui
WORKDIR /eudat/b2share/webui
RUN node_modules/webpack/bin/webpack.js -p

WORKDIR /eudat
ADD . b2share

WORKDIR /eudat/b2share

CMD ["/eudat/b2share.sh"]
