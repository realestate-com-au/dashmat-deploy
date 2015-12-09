#!/bin/bash

if ! which virtualenv 2>&1 > /dev/null; then
  echo "Please install virtualenv and then run this"
  exit 1
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
TMP_DIR="$DIR/.bespin"
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

if [[ ! -f "$DIR/aws/bespin.yml" ]]; then
  echo "Please create a bespin.yml in the aws folder"
  exit 1
fi

version_line=$(egrep "^bespin_version" $DIR/aws/bespin.yml)
if [[ -z $version_line ]]; then
  echo "Please have a bespin_version option in your bespin.yml specifying the version of bespin you need"
  exit 1
fi

required_version="$(echo $version_line | cut -f2 -d:)"

source $TMP_DIR/bin/activate

update=0
if ! python -c "import bespin"; then
  update=1
else
  if ! python <<<"
import sys; from distutils.version import LooseVersion; from bespin import VERSION
if LooseVersion(VERSION) < LooseVersion($required_version):
  sys.exit(1)
" 2>&1 >/dev/null; then
    update=1
  fi
fi

if (($update==1)); then
  required_version=$(python -c "print($required_version.strip())")
  echo "Installing docker-bespin==$required_version"
  pip install pip --upgrade
  pip install argparse
  pip install bespin==$required_version

  # Or if pypi isn't working
  # pip install git+ssh://git@github.com/realestate-com-au/bespin.git
fi

export BESPIN_CONFIG="$DIR/aws/bespin.yml"
bespin "$@"


