#!/usr/bin/env bash
# setup-env.sh requires bash

# Configuration
test -z $TREE && TREE=mozilla-central
SOURCE=/opt/dxr/source/$TREE
BUILD=/opt/dxr/build/$TREE
DXRROOT=/opt/dxr/source/dxr
WWWROOT=/srv/dxr/html
PATH="/opt/dxr/bin/:$PATH"
test -z $VCSPULL && VCSPULL='hg pull'
REMOTE= # dxr.lanedo.com
MAKEFLAGS='-j4 -s V=0'; export MAKEFLAGS
CFLAGS=-std=gnu89; export CFLAGS
# FIXME: disable warning: extension used [-pedantic]
test -z $BUILDCMD && BUILDCMD='make -f client.mk build'

test "`command -v clang`" == "" && echo Failed: clang not found && exit 1
# FIXME: the generic check doesn't work on Debian squeeze
# for i in `egrep -hR '^\s*import [^"]' $DXRROOT/*.py | grep -v dxr | sed -e 's/^[ \t]*//'`; do python -c "$i"; done || echo Failed: Missing Python modules && exit 1
python -c 'import xdg.Mime, sqlite3, subprocess' || echo Failed: Missing Python modules && exit 1

# Source
. $DXRROOT/setup-env.sh $SOURCE $BUILD || exit 1
echo ' '

cd $SOURCE
$SHELL -c "$VCSPULL"
echo ' '

rm -Rf $BUILD # clear, including CSV and configure caches
$SHELL -c "$BUILDCMD" 2>&1 | grep -v 'Unprocessed kind' | grep -v 'clang: warning: argument unused during compilation' || exit 1
NCSV=`find $BUILD -name "*.csv" | wc -l` && test "$NCSV" == "0" && echo Failed: No CSV files && exit 1
echo ' '

# Index
cd $WWWROOT
$DXRROOT/dxr-index.py -t $TREE
NTBL=`echo '.tables' | sqlite3 -init /dev/stdin /$WWWROOT/$TREE/.dxr_xref/*.sqlite | wc -w` && test "$NTBL" != "13" && echo Failed: Missing tables && exit 1

# Split use case
test -n $REMOTE && rsync -aHPz {$WWWROOT,$REMOTE:$WWWROOT}/$TREE-current/

