#!/bin/sh
# Stamp index.html with the version in VERSION and the current build time (run before every commit).
cd "$(dirname "$0")"
v=$(tr -d ' \n' < VERSION); b=$(date '+%Y-%m-%d %H:%M')
sed -i '' -E "s/const APP_VERSION = '[^']*', APP_BUILD = '[^']*'/const APP_VERSION = '$v', APP_BUILD = '$b'/" index.html
grep -o "APP_VERSION = '[^']*', APP_BUILD = '[^']*'" index.html
