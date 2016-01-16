#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT="$DIR/../../"

[[ -z $ENV ]] && echo "Need ENV" && exit 1
[[ -z $BUILD_NUMBER ]] && echo "Need BUILD_NUMBER" && exit 1

export GIT_COMMIT=$(git rev-parse HEAD)

if ! $PROJECT/deploy/bespin.sh publish_artifacts devprod app; then
  echo "Failed to make the artifact!"
  exit 1
fi

