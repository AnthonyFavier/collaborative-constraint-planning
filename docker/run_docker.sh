#!/usr/bin/env bash
image_name=cai_ubuntu_24_04

echo "Starting docker cai_ubuntu_24 container..."
echo $PWD


docker run --privileged --network host \
           --env="DISPLAY=$DISPLAY" \
           --env="QT_X11_NO_MITSHM=1" \
           --volume="$HOME/.Xauthority:$HOME/.Xauthority:rw" \
           --env XAUTHORITY=$HOME/.Xauthority \
           --volume="/tmp/.X11-unix:/tmp/.X11-unix:rw" \
           --volume="$PWD/../:$PWD/../" \
           -v /dev/dri:/dev/dri \
           -v /dev/bus/usb:/dev/bus/usb \
           -v /dev/input:/dev/input \
           --rm -it ${image_name}