FROM elasticsearch:2.2
EXPOSE 9200 9300

RUN cd /usr/share/elasticsearch && \
    yes | ./bin/plugin install mapper-attachments

CMD ["elasticsearch"]
