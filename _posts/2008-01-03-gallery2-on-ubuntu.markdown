---
layout: post
status: publish
published: true
title: Gallery2 on Ubuntu 7.10
excerpt: "<p><a href=\"http://codex.gallery2.org/Gallery2:Download\">Gallery 2</a>
  is a popular web based photo album application.  This details how to install Gallery2
  on Ubuntu 7.10 (Gutsy Gibbon).  These instructions assume you have installed Apache2,
  PHP, and MySQL (as per an install of Ubuntu Server).</p>\r\n\r\n"
wordpress_id: 7
wordpress_url: http://www.thedreaming.org/2008/01/03/gallery2-on-ubuntu/
date: '2008-01-03 14:33:01 -0500'
date_gmt: '2008-01-03 19:33:01 -0500'
tags:
- Ubuntu
- Gallery
comments: []
---
<p><a href="http://codex.gallery2.org/Gallery2:Download">Gallery 2</a> is a popular web based photo album application.  This details how to install Gallery2 on Ubuntu 7.10 (Gutsy Gibbon).  These instructions assume you have installed Apache2, PHP, and MySQL (as per an install of Ubuntu Server).</p>
<p><a id="more"></a><a id="more-7"></a></p>
<h2>Overview</h2>
<ol>
<li>Create Gallery2 Image Storage</li>
<li>Create the Gallery2 Database</li>
<li>Install the PHP GD library and/or NetPBM library</li>
<li>Download and unpack Gallery2</li>
</ol>
<h3>Create Gallery2 Image Storage</h3>
<p>We need to create a directory for Gallery2 to store images in, and this directory needs to be writable by the web-server.  On Ubuntu this means creating a directory owned by the group "www-data", and making the directory group-writable.</p>
<p><code>$ mkdir ~/.gallery2images<br />
$ sudo chgrp www-data ~/.gallery2images<br />
$ chmod 770 ~/.gallery2images<br />
</code></p>
<p>If you're not an admin, you'll have to settle for making the directory world-writable:</p>
<p><code>$ mkdir ~/.gallery2images<br />
$ chmod 777 ~/.gallery2images<br />
</code></p>
<h3>Create the Gallery2 Database</h3>
<p>If you have root access to the mysql database, then:</p>
<p><code>$ mysqladmin -uroot -p create gallery2db<br />
$ mysql gallery2db -uroot -p \<br />
  -e"GRANT ALL ON gallery2db.* TO dbusername@localhost IDENTIFIED BY 'password'"<br />
</code></p>
<p>Replace "dbusername" with your database user name of choice, and "password" with your password of choice.</p>
<p>If you do not have root access, then you need to get your administrator to create a database for you.  You can use an existing database; Gallery prefixes all tables and columns in the database with a string you can configure later in the installation process.</p>
<h3>Install an image processing library</h3>
<p>Gallery2 supports a few different 3rd party image libraries for generating thumbnails, resizing images, and so forth.  ImageMagick  is a popular choice, and is installable from the Ubuntu repository, however at the time of this writing the ImageMagick in the Ubuntu repository is 6.2.4.5, which has known security issues.  So instead we have the choice of the GD library for PHP or NetPBM, both also from the Ubuntu repository.  Install with:</p>
<p><code>$ sudo apt-get update<br />
$ sudo apt-get install php5-gd<br />
$ sudo apt-get install netpbm<br />
$ sudo /etc/init.d/apache2 restart<br />
</code></p>
<p>The restart of Apache2 is required so PHP will find the GD library.</p>
<p>If you don't have administrator access to the Ubuntu machine, you'll need to get your administrator to install one of these libraries.</p>
<h3>Download and unpack Gallery2</h3>
<p>Go grab the latest <a href="http://codex.gallery2.org/Gallery2:Download">Gallery 2</a> .  In my case, this is 2.2.4.  Go to the directory where you want to install gallery and unpack it.  This must be a directory which is visible on the web:</p>
<p><code>$ cd public_html<br />
$ tar xvzf ../gallery-2.2.4-typical.tar.gz</code></p>
<p>And then point your browser at the install directory.  From here you can pretty much follow the instructions given by the installer.  If you need additional help, have a look at the <a href="http://codex.gallery2.org/Gallery2:How_do_I_Install_Gallery2#Installing_Gallery_2_2">instructions from the Gallery2 website</a>.</p>
