FROM centos:7
EXPOSE 5000

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-8.noarch.rpm && \
    yum -y update && \
    yum -y install wget python34 python34-devel npm supervisor git libffi-devel python-devel libxml2-devel libxml2 libxslt-devel zlib1g-devel libxslt

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.4 get-pip.py && \
    pip3 install --upgrade pip

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/b2share.git --branch evolution

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_ACCOUNTS_SESSION_REDIS_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SECRET_KEY="sX5BwQI8cZQmxmM6RfI08zSDm6tPt8Tc"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"

# # only use this for the staging server
# ENV SSL_CERT_FILE="staging_b2access.pem"

WORKDIR /eudat/b2share/webui
RUN npm install --unsafe-perm && \
    node_modules/webpack/bin/webpack.js -p

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git  \
    && cd public-license-selector                                           \
    && npm install
WORKDIR /eudat/public-license-selector

# this next RUN is just a workaround for the old version of node on centos7
# without it, the npm run build fails when compiling less files
RUN mv webpack.config.js webpack.config.js.0                                \
    && echo "require('es6-promise').polyfill();" > webpack.config.js        \
    && cat webpack.config.js.0 >> webpack.config.js                         \
    && npm install es6-promise

RUN npm run build                                                           \
    && mkdir -p ../b2share/webui/app/vendors                                \
    && cp dist/license-selector.* ../b2share/webui/app/vendors/

WORKDIR /eudat/b2share
RUN pip install requirements-builder
RUN requirements-builder --level=min setup.py > lowest-requirements.txt
RUN pip install -r lowest-requirements.txt
RUN pip install -e .

WORKDIR /eudat/b2share/demo
RUN pip install -e .

COPY b2share.sh /eudat/
COPY supervisord.conf /etc/

RUN systemctl disable firewalld

WORKDIR /eudat/b2share

CMD ["/usr/bin/supervisord"]
