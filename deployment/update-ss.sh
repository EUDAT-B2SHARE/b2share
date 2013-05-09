#!/bin/bash

# update to the latest version
(cd /home/admin/src/simplestore && sudo -u admin git pull origin demo)

# deploy
(cd /home/admin/src/simplestore && /home/admin/src/simplestore/deploy_overlay.sh)
