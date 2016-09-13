VERSION=`cat ../b2share/version.py | grep __version__ | cut -f2 -d'"'`
echo export const VERSION=\"$VERSION\" > ./src/version.js
echo export const GIT_COMMIT=\"$GIT_COMMIT\" >> ./src/version.js
