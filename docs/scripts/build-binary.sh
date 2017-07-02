#!/bin/bash

set -ex

VENV=.tox/py35

mkdir -p `pwd`/dist
chmod 777 `pwd`/dist

$VENV/bin/pip install -q -r requirements.txt
$VENV/bin/pip install -q pyinstaller

$VENV/bin/pyinstaller pyplanet.spec
