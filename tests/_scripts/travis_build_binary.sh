#!/bin/bash

# Only when in integration py35
if [[ ${TOXENV} == "py35-integration-mysql" ]]; then
  echo "Building binary file..."
else
  exit 0
fi

set -ex

docs/scripts/build-binary.sh
