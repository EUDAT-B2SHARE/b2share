
### Fetch source and install B2SHARE + dependencies
* Clone latest master of EUDAT-B2SHARE/b2share  
  `git clone https://github.com/EUDAT-B2SHARE/b2share.git fresh-devenv`

* NOTE: All commands are expected to be run in repo root.

* Create a virtualenv. Use Python 3.6
  NOTE: Remember to activate virtualenv for all terminals you open.  
  <DEPENDS_ON_YOUR_OWN_TOOLS_SET>

* If Linux is used, cryptography and lxml require additional build dependencies
  For Ubuntu 18.04 install these packages:  
  `$ sudo apt-get install build-essential libssl1.0 libssl-dev libffi-dev python3-dev`
  `$ sudo apt-get install libxml2-dev libxslt-dev`

* Install B2SHARE dependencies  
  `$ pip install -r requirements.txt`

* Install B2SHARE in editable mode  
  `$ pip install -e .`

* [OPTIONAL] Build B2SHARE WebUI if needed
  NOTE: You need to have NodeJS installed. NodeJS v12 is known to work.  
  `$ cd webui`  
  `$ npm install --unsafe-perm`  
  `$ cd ..`


### Start support services and initialize B2SHARE 

* Source RC file for envvar config variables.  
  Customize as needed for your system (e.g. 'B2SHARE_UI_PATH')  
  NOTE: Remember do this for all terminals you open.  
  `$ source ./devenvrc`
  
* Start support services (postgresql, redis, rabbitmq, elasticsearch)  
  `$ docker-compose -f docker-compose-dev.yml up -d`

* Initialize B2SHARE (Create SQL structures, ES indices, etc.)  
  `$ b2share db init`  
  `$ b2share index init`  
  `$ b2share upgrade run -v`


### Load demo data OR initialize B2SHARE file storage
* Load demo data
  (Also initialises file storage location. Default is Flask instance-folder which can be found under virtualenv '/var' folder.)  
  `$ pip install -e ./demo/`  
  `$ b2share demo load_data`

* Init file storage location  
  (This is not needed and will fail if demo data has been loaded)  
  Note: Set files storage path some proper path in your system:  
  E.g. subfolder of repo root. (Remember to create the subfolder first)  
  `$ B2SHARE_FILES_STORAGE_PATH=file://$PWD/files-storage` 
  `$ b2share files add-location 'local' $B2SHARE_FILES_STORAGE_PATH --default`


### Start B2SHARE backend , Celery and Web-UI
* Start B2SHARE backend (i.e. `flask run`)  
  `$ b2share run --port=5000 --host=0.0.0.0 --with-threads`  
  In case debug mode and source watch:  
  `$ FLASK_ENV=development FLASK_DEBUG=1 DEBUG=True b2share run --port 5000 --host=0.0.0.0 --with-threads`

* [OPTIONAL] Start Celery to enable background jobs  
  (e.g. statistics gathering with Invenio-Stats)  
  NOTE: 'B2SHARE_REPO_ROOT' envvar is set in 'devenvrc' -file  
  `$ celery worker -D -E -A b2share.celery -l DEBUG --workdir=$B2SHARE_REPO_ROOT`  
  `$ celery beat -A b2share.celery --pidfile= --workdir=$B2SHARE_REPO_ROOT --loglevel="DEBUG"`

* [OPTIONAL] Start B2SHARE WebUI if needed 
  (i.e. `webpack devserver`)  
  `$ cd webui`  
  `$ ./node_modules/webpack/bin/webpack.js --config webpack.config.devel.js -dw`


### Re-init
* In case reinit is needed, following commands must be run.
  These remove all data from postgres and elasticsearch and reinit.  
  Remember to load demo data again, if needed.  
  `$ b2share db destroy --yes-i-know`  
  `$ b2share index destroy --yes-i-know`  
  `$ b2share db init && b2share index init && b2share upgrade run -v`


### Shutdown

* No special shutdown order should be required, but optimally:
  - Shutdown WebUI
  - Shutdown B2SHARE backend
  - Shutdown Celery  
    `$ ps auxww | awk '/celery worker/ {print $2}' | xargs kill -9`  
    See https://docs.celeryproject.org/en/stable/userguide/workers.html#stopping-the-worker for more info

  - Shutdown support services  
    `$ docker-compose -f docker-compose-dev.yml down`  
    (if you want to remove persistent data volumes run)  
    `$ docker-compose -f docker-compose-dev.yml down -v`


### Start up when you continue working  
(init done, persistent data for support services available)

* Following order has been know to work
  - Start support services
  - Start B2SHARE backend
  - Start Celery if needed
  - Start WebUI if needed
