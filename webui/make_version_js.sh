VERSION=`cat ../b2share/version.py | grep __version__ | cut -f2 -d'"'`
echo export const VERSION=\"$VERSION\" > ./src/version.js

GIT_COMMIT=`git rev-parse --short HEAD`
echo export const GIT_COMMIT=\"$GIT_COMMIT\" >> ./src/version.js
