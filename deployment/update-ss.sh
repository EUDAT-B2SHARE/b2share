#!/bin/bash

B2SHARE_SRC=/home/admin/src/b2share

# update to the latest version
(cd $B2SHARE_SRC && sudo -u admin git pull origin master)
(cd $B2SHARE_SRC && sudo -u admin pip install -r requirements.txt)

# deploy
(cd $B2SHARE_SRC && $B2SHARE_SRC/deployment/deploy_overlay.sh)
