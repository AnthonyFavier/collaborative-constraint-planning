#!/usr/bin/env bash
image_name=cai_ubuntu_24_04

xhost +local:docker

echo " "

echo "Starting docker cai_ubuntu_24 container..."
echo $PWD

source ../.env

echo " "

docker run --privileged --network host \
           --env="DISPLAY=$DISPLAY" \
           --env="QT_X11_NO_MITSHM=1" \
           --env XAUTHORITY=$HOME/.Xauthority \
           -v $HOME/.Xauthority:$HOME/.Xauthority:rw \
           -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
           -v /dev/dri:/dev/dri \
           -v /dev/bus/usb:/dev/bus/usb \
           -v /dev/input:/dev/input \
           -v $PWD/../:$PWD/../ \
           -v $PDSIM_INSTANCE_PATH:$PDSIM_INSTANCE_PATH \
           --rm -it ${image_name}