#!/bin/sh

cd ~/git/qcif-extract
. venv/bin/activate
. /media/scrawley/CARTMAN/admin.sh

FLAGS="-c /media/scrawley/CARTMAN/mosaic.cfg"

YEAR=$1
MONTH=$2

set -x
extract/extract.py $FLAGS general \
&& extract/extract.py $FLAGS managers --legacy \
&& extract/extract.py $FLAGS project-usage --year $YEAR --month $MONTH \
&& extract/extract.py $FLAGS instance-usage --year $YEAR --month $MONTH \
&& extract/extract.py $FLAGS instance-usage --qriscloud --year $YEAR --month $MONTH 

