FROM centos:7
EXPOSE 5000

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/e/epel-release-7-5.noarch.rpm && \
    yum -y update && \
    yum -y install wget python34 python34-devel npm supervisor git libffi-devel

WORKDIR /tmp
RUN wget https://bootstrap.pypa.io/get-pip.py && \
    python3.4 get-pip.py && \
    pip3 install --upgrade pip

WORKDIR /eudat
RUN git clone https://github.com/EUDAT-B2SHARE/b2share.git --branch evolution b2share

ENV LANG=en_US.UTF-8
ENV DB_NAME="b2share-evolution"
ENV B2SHARE_UI_PATH="/eudat/b2share/webui/app"
ENV B2SHARE_BROKER_URL="redis://redis:6379/0"
ENV B2SHARE_CELERY_RESULT_BACKEND="redis://redis:6379/1"
ENV B2SHARE_SECRET_KEY="sX5BwQI8cZQmxmM6RfI08zSDm6tPt8Tc"
ENV B2SHARE_SEARCH_ELASTIC_HOSTS="elasticsearch:9200"
ENV B2SHARE_SERVER_NAME="0.0.0.0:5000"

WORKDIR /eudat/b2share/webui
RUN npm install && \
    node_modules/webpack/bin/webpack.js -p

WORKDIR /eudat/b2share
RUN pip install -r requirements.txt

WORKDIR /eudat/b2share/demo
RUN pip install -e .

COPY b2share.sh /eudat/
COPY supervisord.conf /etc/

RUN systemctl disable firewalld

WORKDIR /eudat/b2share

CMD ["/usr/bin/supervisord"]
