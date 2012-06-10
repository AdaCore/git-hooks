#!/bin/bash
# Generate a coverage report

# Usage: ./coverage.sh [--user] [testsuite_options]
# if --user, use gnatpython installed in user site

root=`dirname $0`

export COVERAGE_PROCESS_START=`pwd`/coverage.rc
export COVERAGE_DIR=`pwd`
export GIT_HOOKS_DIR="$root/../hooks"
export GIT_HOOKS_MODULES="$GIT_HOOKS_DIR/*.py"

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
coverage combine
coverage report "$GIT_HOOKS_MODULES"
coverage html "$GIT_HOOKS_MODULES"
perl -pi -e "s;$GIT_HOOKS_DIR/;;" htmlcov/*
