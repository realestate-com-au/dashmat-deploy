#!/bin/bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT="$DIR/../../"

[[ -z $ENV ]] && echo "Need ENV" && exit 1
[[ -z $BUILD_NUMBER ]] && echo "Need BUILD_NUMBER" && exit 1

$PROJECT/deploy/bespin.sh sanity_check $ENV app

