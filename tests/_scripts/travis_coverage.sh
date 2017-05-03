#!/usr/bin/env bash

# Check if we should run at all
if [[ ${TOXENV} == *"integration"* ]]; then
  TYPE_TEST="integration"
else
  TYPE_TEST="unittests"
fi

BEFORE_PWD=`pwd`
cd "$(dirname "$0")"
cd ../../
cd src
# From now we are in the project source folder.

bash <(curl -s https://codecov.io/bash) -e TOX_ENV -F ${TYPE_TEST}
