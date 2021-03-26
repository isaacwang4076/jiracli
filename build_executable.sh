#!/bin/bash
set -ex
cd "$(dirname "$0")"
if [ -z "$1" ]
  then
    echo "No module specified"
    exit 1
fi
project=$1
cxfreeze ${project}/main.py --target-dir ${project}/build/dist --target-name ${project}
zip -r ${project}/build/${project}.zip ${project}/build/dist
