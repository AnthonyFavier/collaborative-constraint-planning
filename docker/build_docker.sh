#!/usr/bin/env bash
image_name=cai_ubuntu_24_04

ln ../requirements.txt requirements.txt

docker build \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g) \
    --build-arg UNAME=$(whoami) \
    --build-arg REPO_PATH=$(pwd)/.. \
    -t ${image_name} $(dirname "$0")/