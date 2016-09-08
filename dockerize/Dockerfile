FROM centos:7
EXPOSE 5000

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm && \
    yum -y update && \
    yum -y install wget python34 python34-devel npm supervisor git libffi-devel python-devel libxml2-devel libxml2 libxslt-devel zlib1g-devel libxslt

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.4 get-pip.py && \
    pip3 install --upgrade pip

# RUN git clone https://github.com/EUDAT-B2SHARE/b2share.git --branch evolution
# ADD . b2share

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SECRET_KEY="sX5BwQI8cZQmxmM6RfI08zSDm6tPt8Tc"
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
# Install python module and dependencies
#

WORKDIR /eudat/b2share
ADD setup.py setup.py
ADD b2share/version.py b2share/version.py

RUN pip install requirements-builder
RUN requirements-builder --level=min setup.py > lowest-requirements.txt
RUN pip install -r lowest-requirements.txt
RUN pip install -e .

WORKDIR /eudat/b2share/demo
ADD demo/setup.py setup.py
RUN pip install -e .

COPY dockerize/b2share.sh /eudat/
COPY dockerize/supervisord.conf /etc/

#
# Copy the rest of B2Share files
#

WORKDIR /eudat/b2share
ADD webui webui
WORKDIR /eudat/b2share/webui
ARG GIT_COMMIT
ENV GIT_COMMIT="$GIT_COMMIT"
RUN node_modules/webpack/bin/webpack.js -p

WORKDIR /eudat
ADD . b2share

WORKDIR /eudat/b2share
CMD ["/usr/bin/supervisord"]
