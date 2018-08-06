#!/bin/sh

cd ~/git/qcif-extract
. venv/bin/activate
. /media/scrawley/CARTMAN/admin.sh

# See README.md
export OS_COMPUTE_API_VERSION=2.40

FLAGS="-c /media/scrawley/CARTMAN/mosaic.cfg"

YEAR=$1
MONTH=$2

set -x
extract/extract.py $FLAGS general \
&& extract/extract.py $FLAGS managers \
&& extract/extract.py $FLAGS project-usage --year $YEAR --month $MONTH \
&& extract/extract.py $FLAGS instance-usage --year $YEAR --month $MONTH \
&& extract/extract.py $FLAGS instance-usage --qriscloud --year $YEAR --month $MONTH 

