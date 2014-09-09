---
layout: post
status: publish
published: true
title: Converting iTunes Playlists to m3u Files with XSLT
wordpress_id: 5
wordpress_url: http://www.thedreaming.org/2007/12/12/converting-itunes-playlists-to-m3u-files-with-xslt/
redirect_from:
  - /2007/12/12/converting-itunes-playlists-to-m3u-files-with-xslt/
date: '2007-12-12 11:45:05 -0500'
date_gmt: '2007-12-12 16:45:05 -0500'
tags:
- xslt
- iTunes
- mp3
comments: []
---
I've been playing around with [Firefly Media Server](http://en.wikipedia.org/wiki/Firefly_Media_Server) a bit of late, and I needed a good way to convert my existing iTunes playlists into m3u files which Firefly would understand.  Since iTunes exports XML playlist files, and since I've been meaning to learn some XSLT, I thought I'd give an XSLT converter a try.

The XSLT relies on features found in XSTL 2.0, so you'll need a 2.0 compatible processor, like [Saxon](http://saxon.sourceforge.net).  To use Saxon, you'll also need Java installed, and Saxon is command-line only.

To use with Saxon, export your playlist from iTunes as an XML file, and then run:

    java -jar saxon9.jar -s:MyPlaylist.xml -xsl:itunesToM3u.xsl -o:MyPlaylist.m3u

This will strip out any escaped values in the URLs in the iTunes XML file, and strip off the leading "file://localhost/" from each file.  Enjoy!

Get it here: <a href="{{ site.baseurl }}/files/itunesToM3u.xsl" download>itunesToM3u.xsl</a>
