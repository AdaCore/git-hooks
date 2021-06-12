#!/bin/bash
# Generate a coverage report

# Usage: ./coverage.sh [--user] [testsuite_options]
# if --user, use gnatpython installed in user site

root=`dirname $0`

export COVERAGE_PROCESS_START=`pwd`/coverage.rc
export COVERAGE_DIR=`pwd`

rm -f .coverage*

if [ "$PYTHON" = "" ]; then
   PYTHON=python
fi

python=`which $PYTHON`
mkdir -p sitecustomize
export PYTHONPATH=`pwd`/sitecustomize:$PYTHONPATH

cat <<EOF > sitecustomize/sitecustomize.py
import coverage; coverage.process_startup()
EOF

cat <<EOF > coverage.rc
[run]
cover_pylib = True
parallel = True
EOF


$root/run-testsuite $@

GIT_HOOKS_DIR="$root/../hooks"
# ??? Exclude hooks/updates/sendmail.py from the list of modules,
# since it is a copy of gnatpython's sendmail module.
# This is going to be necessary until we have a gnatpython release
# which provides the sendmail module.
GIT_HOOKS_MODULES=`find $GIT_HOOKS_DIR -name '*.py' -print | grep -v hooks/updates/sendmail.py`
coverage combine
coverage report --rcfile=coverage.rc $GIT_HOOKS_MODULES
coverage html --rcfile=coverage.rc $GIT_HOOKS_MODULES
perl -pi -e "s;$GIT_HOOKS_DIR/;;" htmlcov/*
