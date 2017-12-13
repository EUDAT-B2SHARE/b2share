FROM dinossimpson/b2safe-integration
WORKDIR /eudat/b2share/b2share4
RUN git clone https://github.com/dinosk/b2share.git
WORKDIR /eudat/b2share/b2share4/b2share
RUN git checkout b2safe-pids
RUN pip install -e .[all]
CMD ["/eudat/b2share.sh"]
