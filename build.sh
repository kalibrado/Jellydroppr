#!/usr/bin/env bash

tag=$1

docker build -t ldfe/jellydroppr:$tag .


docker push ldfe/jellydroppr:$tag-release

