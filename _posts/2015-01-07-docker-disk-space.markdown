---
title: "Removing Stale Docker Images"
tags:
- docker
---
If you do any kind of "development" in docker land, you'll be creating new images all the time.  The latest versions of Docker no longer use Union FS, and instead use devicemapper to merge together all these different "layers".  Devicemapper generates rather largish files, so if you're not careful, you can quickly run out of disk space (especially if you're on an EC2 instance with a tiny 8GB drive.)

<!--more-->
To see what images you have:

    sudo docker images

The "virtual size" column is the size of the whole image, but this includes some parent images which may be shared between images.  That said, we still want to delete images we're not using (with `docker rmi`).  Note that docker will refuse to delete images that are in use by a container (even if the container is stopped), so it's safe to do:

    sudo docker images -q | xargs sudo docker rmi

This tries to delete all the images, and will probably give you a ton of warnings.  If you want something slightly more nuanced:

    for i in `sudo docker images|grep \<none\>|awk '{print $3}'`;do sudo docker rmi $i;done

which will delete only images with "&lt;none&gt;" in their tag or repository columns.

Update: Found this slick command on [stack overflow](http://stackoverflow.com/questions/28085067/docker-images-eats-up-lots-of-space?lq=1):

    sudo docker rmi $(sudo docker images -q -f dangling=true)

Update 2019-04: This is built into docker now:

    # Delete stopped containers:
    docker container prune --force

    # Delete stale images
    docker image prune -a --force
