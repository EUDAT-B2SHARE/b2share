FROM docker_b2safe3
WORKDIR /eudat/b2share/b2share3
RUN git clone https://github.com/dinosk/b2share.git
WORKDIR /eudat/b2share/b2share3/b2share
RUN git checkout docker-b2safe
RUN pip install -e .[all]
CMD ["/eudat/b2share.sh"]
