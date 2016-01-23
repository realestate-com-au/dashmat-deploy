#!/bin/bash

if ! which virtualenv 2>&1 > /dev/null; then
  echo "Please install virtualenv and then run this"
  exit 1
fi

# This is mainly for the docker container making artifacts
export PATH=/bin:/usr/bin:/usr/local/bin:/usr/sbin:/usr/local/sbin

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TMP_DIR="$DIR/.dashmat"
if [[ ! -d $TMP_DIR ]]; then
  opts=""
  if ! which python3; then
    echo "Please install python3"
    exit 1
  else
    question="
import sys
if sys.version.startswith(\"3.4\"): sys.exit(1)
    "
    if python -c "$question"; then
      opts=" -p $(which python3)"
    fi
  fi

  if ! virtualenv $opts $TMP_DIR; then
    echo "Couldn't make the virtualenv :("
    rm -rf $TMP_DIR
    exit 1
  fi
fi

required_version=0.2.7

source $TMP_DIR/bin/activate
export PYTHONPATH=$PYTHONPATH:$DIR

if ! $IGNORE_PIP || [[ -z ${IGNORE_PIP} ]]; then
  pip install pip --upgrade
  pip install dashmat==$required_version
  pip install -r <($TMP_DIR/bin/dashmat requirements --config $DIR/config.yml)
fi

export DASHMAT_CONFIG=$DIR/config.yml
dashmat "$@"
