# Based on https://github.com/docker-library/elasticsearch/blob/8e87587ac5d6b44a8382a229162c88e65618c30a/2.4/Dockerfile
FROM docker.io/openjdk:8-jre

# grab gosu for easy step-down from root
ENV GOSU_VERSION 1.10
RUN set -x \
	&& wget -O /usr/local/bin/gosu "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture)" \
	&& wget -O /usr/local/bin/gosu.asc "https://github.com/tianon/gosu/releases/download/$GOSU_VERSION/gosu-$(dpkg --print-architecture).asc" \
	&& export GNUPGHOME="$(mktemp -d)" \
	&& gpg --keyserver ha.pool.sks-keyservers.net --recv-keys B42F6819007F00F88E364FD4036A9C25BF357DD4 \
	&& gpg --batch --verify /usr/local/bin/gosu.asc /usr/local/bin/gosu \
	&& rm -rf "$GNUPGHOME" /usr/local/bin/gosu.asc \
	&& chmod +x /usr/local/bin/gosu \
	&& gosu nobody true

RUN set -ex; \
# https://artifacts.elastic.co/GPG-KEY-elasticsearch
        key='46095ACC8548582C1A2699A9D27D666CD88E42B4'; \
        export GNUPGHOME="$(mktemp -d)"; \
        gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key"; \
        gpg --export "$key" > /etc/apt/trusted.gpg.d/elastic.gpg; \
        rm -rf "$GNUPGHOME"; \
        apt-key list

# https://www.elastic.co/guide/en/elasticsearch/reference/current/setup-repositories.html
# https://www.elastic.co/guide/en/elasticsearch/reference/5.0/deb.html
RUN set -x \
        && apt-get update && apt-get install -y --no-install-recommends apt-transport-https && rm -rf /var/lib/apt/lists/* \
        && echo 'deb http://packages.elasticsearch.org/elasticsearch/2.x/debian stable main' > /etc/apt/sources.list.d/elasticsearch.list

ENV ELASTICSEARCH_VERSION 2.4.6
ENV ELASTICSEARCH_DEB_VERSION 2.4.6

RUN set -x \
        \
# don't allow the package to install its sysctl file (causes the install to fail)
# Failed to write '262144' to '/proc/sys/vm/max_map_count': Read-only file system
        && dpkg-divert --rename /usr/lib/sysctl.d/elasticsearch.conf \
        \
        && apt-get update \
        && apt-get install -y --no-install-recommends "elasticsearch=$ELASTICSEARCH_DEB_VERSION" \
        && rm -rf /var/lib/apt/lists/*

ENV PATH /usr/share/elasticsearch/bin:$PATH

WORKDIR /usr/share/elasticsearch

RUN set -ex \
        && for path in \
                ./data \
                ./logs \
                ./config \
                ./config/scripts \
                /usr/share/elasticsearch/logs \
                /usr/share/elasticsearch/data \
        ; do \
                mkdir -p "$path"; \
                chown -R elasticsearch:elasticsearch "$path"; \
        done

COPY config ./config

VOLUME /usr/share/elasticsearch/config
VOLUME /usr/share/elasticsearch/data

# Install mapper attachments required B2SHARE
RUN cd /usr/share/elasticsearch && \
    ./bin/plugin install -b mapper-attachments

COPY docker-entrypoint.sh /

EXPOSE 9200 9300

USER elasticsearch

CMD ["elasticsearch"]
