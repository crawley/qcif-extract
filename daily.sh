#!/bin/sh

cd ~/git/qcif-extract
. venv/bin/activate
. /media/scrawley/CARTMAN/admin.sh

# See README.md
export OS_COMPUTE_API_VERSION=2.40

FLAGS="-c /media/scrawley/CARTMAN/mosaic.cfg"

extract/extract.py $FLAGS members \
&& extract/extract.py $FLAGS managers \

