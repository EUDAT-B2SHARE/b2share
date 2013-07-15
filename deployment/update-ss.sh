#!/bin/bash

# update to the latest version
(cd /home/admin/src/simplestore && sudo -u admin git pull origin master)
(cd /home/admin/src/simplestore && sudo -u admin pip install -r requirements.txt)

# deploy
(cd /home/admin/src/simplestore && /home/admin/src/simplestore/deployment/deploy_overlay.sh)
