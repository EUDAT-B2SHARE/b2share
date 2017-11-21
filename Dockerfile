FROM centos:7
EXPOSE 5000

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-10.noarch.rpm

RUN yum -y update

RUN yum -y install wget gcc-c++ openssl-devel uwsgi-plugin-python3 \
                   postgresql-devel python34 python34-devel supervisor \
                   git uwsgi libffi-devel python-devel libxml2-devel libxml2 \
                   libxslt-devel zlib1g-dev libxslt http-parser npm

# install locale
RUN localedef -c -f UTF-8 -i en_US en_US.UTF-8

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.4 get-pip.py
RUN pip3 install --upgrade pip

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"

#
# Install public-license-selector
#

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git
WORKDIR /eudat/public-license-selector
RUN npm install

# this next RUN is just a workaround for the old version of node on centos7
# without it, the npm run build fails when compiling less files
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
RUN git clone https://github.com/dinosk/b2share.git
WORKDIR /eudat/b2share/b2share
RUN git checkout b2safe-pids
RUN pip install .
COPY dockerize/records /usr/lib/python3.4/site-packages/b2share/modules/records/mappings/records
COPY dockerize/deposits /usr/lib/python3.4/site-packages/b2share/modules/deposit/mappings/deposits
COPY b2share/modules/schemas/root_schemas /usr/lib/python3.4/site-packages/b2share/modules/schemas/root_schemas

WORKDIR /eudat/b2share/demo
ADD demo/setup.py setup.py
RUN pip install .

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
