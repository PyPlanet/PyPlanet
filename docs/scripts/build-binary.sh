#!/bin/bash

mkdir -p `pwd`/dist
chmod 777 `pwd`/dist

pip install -q -r requirements.txt
pip install -q pyinstaller

pyinstaller pyplanet.spec
