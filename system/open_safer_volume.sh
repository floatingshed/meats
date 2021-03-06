#!/bin/bash

# this is for use when the image is already created

if [ -z "$1" ] ; then
    file=image_.bin
else
    file="$1"
fi

if [ ! -f $file ] ; then
    echo "File '$file' does not exist. Please run create_safer_volume.sh $file first."
    exit
fi

if [ "$2" = "old" ] ; then
    options="--type plain -c aes-cbc-plain"
fi

echo "Opening file as /dev/mapper/$file"
sudo cryptsetup open $file $file $options

echo "Preparing mount point /mnt/$file"
sudo mkdir /mnt/$file

me=`whoami`
echo "Mounting for user $me"
sudo mount /dev/mapper/$file /mnt/$file
sudo chown $me /mnt/$mnt
