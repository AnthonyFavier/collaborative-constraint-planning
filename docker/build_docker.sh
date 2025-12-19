#!/usr/bin/env bash
image_name=cai_ubuntu_24_04

docker build \
    --build-arg UID=$(id -u) \
    --build-arg GID=$(id -g) \
    --build-arg UNAME=$(whoami) \
    --build-arg REPO_PATH=$(pwd)/.. \
    -t ${image_name} $(dirname "$0")/


docker run --rm -v $PWD/../:$PWD/../ ${image_name} bash -c "source install.sh"
# Note: ignore the error /entrypoint.sh: line 4: env_cai/bin/activate: No such file or directory