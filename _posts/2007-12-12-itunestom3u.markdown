---
layout: post
status: publish
published: true
title: Converting iTunes Playlists to m3u Files with XSLT
author: Jason Walton
wordpress_id: 5
wordpress_url: http://www.thedreaming.org/2007/12/12/converting-itunes-playlists-to-m3u-files-with-xslt/
date: '2007-12-12 11:45:05 -0500'
date_gmt: '2007-12-12 16:45:05 -0500'
categories:
- Software
tags:
- xslt
- iTunes
- mp3
comments: []
---
<p>I've been playing around with <a href="http://www.fireflymediaserver.org">Firefly Media Server</a> a bit of late, and I needed a good way to convert my existing iTunes playlists into m3u files which Firefly would understand.  Since iTunes exports XML playlist files, and since I've been meaning to learn some XSLT, I thought I'd give an XSLT converter a try.</p>
<p>The XSLT relies on features found in XSTL 2.0, so you'll need a 2.0 compatible processor, like <a href="http://saxon.sourceforge.net">Saxon</a>.  To use Saxon, you'll also need Java installed, and Saxon is command-line only.</p>
<p>To use with Saxon, export your playlist from iTunes as an XML file, and then run:</p>
<div class="code"><nobr>java -jar saxon9.jar -s:MyPlaylist.xml -xsl:itunesToM3u.xsl -o:MyPlaylist.m3u<br />
  </nobr></div>
<p>This will strip out any escaped values in the URLs in the iTunes XML file, and strip off the leading "file://localhost/" from each file.  Enjoy!</p>
<p>Get it here: <a href="http://www.thedreaming.org/code/itunesToM3u/itunesToM3u.xsl">itunesToM3u.xsl</a></p>
