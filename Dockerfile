FROM node:latest as build-deps

# Build License Selector

WORKDIR /tmp

RUN git clone https://github.com/EUDAT-B2SHARE/public-license-selector.git
WORKDIR /tmp/public-license-selector
RUN npm install --unsafe-perm
#RUN npm audit fix --force
RUN npm run build

# Build B2Share App

WORKDIR /opt

ADD webui/src src
ADD webui/package.json .
ADD webui/webpack.config.js .

RUN echo "echo 'Files copied !'" > ./copy_files.sh && chmod a+x ./copy_files.sh

RUN mv webpack.config.js webpack.config.js.0
RUN echo "require('es6-promise').polyfill();" > webpack.config.js
RUN cat webpack.config.js.0 >> webpack.config.js
RUN npm install es6-promise
RUN npm install --unsafe-perm

RUN node_modules/webpack/bin/webpack.js -p

FROM centos:7

RUN rpm -iUvh http://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/e/epel-release-7-13.noarch.rpm

RUN yum -y update
RUN yum -y groupinstall "Development tools"
RUN yum -y install wget gcc-c++ openssl-devel \
                   postgresql-devel mysql-devel \
                   git libffi-devel libxml2-devel libxml2 \
                   libxslt-devel zlib1g-dev libxslt http-parser uwsgi

# Install Python...

ENV PYTHON_VER=3.6
ENV PYTHON_PRG=/usr/bin/python${PYTHON_VER}
ENV PYTHON_ENV=/opt/.venv
ENV PYTHON_LIB=${VIRTUAL_ENV}/lib/python${PYTHON_VER}

RUN echo -e \
    "\tPYTHON VERSION : $PYTHON_VER\n" \
    "\tPYTHON PROGRAM : $PYTHON_PRG\n" \
    "\tPYTHON VIRTUAL : $PYTHON_ENV\n" \
    "\tPYTHON LIBRARY : $PYTHON_LIB\n"

RUN yum -y install python${PYTHON_VER//.} python${PYTHON_VER//.}-pip python${PYTHON_VER//.}-devel python${PYTHON_VER//.}-virtualenv
RUN yum -y install uwsgi-plugin-python${PYTHON_VER//.}

RUN ${PYTHON_PRG} -m virtualenv --python=${PYTHON_PRG} ${PYTHON_ENV}
ENV PATH="$PYTHON_ENV/bin:$PATH"

# install locale
RUN localedef -c -f UTF-8 -i en_US en_US.UTF-8
ENV LC_ALL=en_US.utf-8
ENV LANG=en_US.utf-8

# Prepare application backend...

ENV B2SHARE_INSTANCE_PATH=/opt/var

WORKDIR /opt/app

ADD MANIFEST.in .
ADD entry_points.txt .
ADD requirements.txt .
ADD README.rst .
ADD setup.py .
ADD setup.cfg .
ADD b2share b2share

RUN pip install -r requirements.txt

# Prepare application frontend...

COPY webui/app b2share/modules/b2share_main/static

RUN mv b2share/modules/b2share_main/static/index.html b2share/modules/b2share_main/templates/b2share_main/page.html

# Add generated files into lib sub directories...
COPY --from=build-deps /opt/app/b2share-bundle.* b2share/modules/b2share_main/static/
COPY --from=build-deps /opt/node_modules/bootstrap/dist/css/bootstrap.min.* b2share/modules/b2share_main/static/lib/css/
COPY --from=build-deps /opt/node_modules/bootstrap-grid/dist/grid.min.css b2share/modules/b2share_main/static/lib/css/bootstrap-grid.min.css
COPY --from=build-deps /opt/node_modules/react-widgets/dist/css/* b2share/modules/b2share_main/static/lib/css/
COPY --from=build-deps /opt/node_modules/font-awesome/css/* b2share/modules/b2share_main/static/lib/css/
COPY --from=build-deps /opt/node_modules/react-toggle/style.css b2share/modules/b2share_main/static/lib/css/toggle-style.css
COPY --from=build-deps /opt/node_modules/bootstrap/dist/fonts/* b2share/modules/b2share_main/static/lib/fonts/
COPY --from=build-deps /opt/node_modules/react-widgets/dist/fonts/* b2share/modules/b2share_main/static/lib/fonts/
COPY --from=build-deps /opt/node_modules/font-awesome/* b2share/modules/b2share_main/static/lib/fonts/
COPY --from=build-deps /opt/node_modules/react-widgets/dist/img/* b2share/modules/b2share_main/static/lib/img/

# Add License Selector
COPY --from=build-deps /tmp/public-license-selector/dist/license-selector.* b2share/modules/b2share_main/static/vendors/

RUN pip install --upgrade pip
RUN pip install .[all,postgresql,elasticsearch7]

# Optional for debugging....
RUN pip install flask_DebugToolBar

EXPOSE 5000

CMD ["b2share"]
