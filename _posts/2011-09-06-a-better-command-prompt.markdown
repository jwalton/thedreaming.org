---
layout: post
status: publish
published: true
title: A Better Command Prompt
author: Jason Walton
excerpt: "If you've spent much time doing development work on Linux or Max OS X, and
  you suddenly find yourself stuck doing development work on a Windows machine, one
  of the things you'll quickly learn to hate is the Windows command prompt.  You can't
  resize the command prompt window, and cut-and-paste is a bit of a pain.  You can
  use <a href=\"http://x.cygwin.com/\">Cygwin/X</a> to get yourself a <a href=\"http://www.zieg.com/faqs/cygwin/#cygwin_rxvt\">genuine
  xterm window</a>, but Cygwin is a little heavy weight, and not all Windows console
  programs will work properly in Cygwin due to differences in the way POSIX handles
  stdout.\r\n\r\nEnter <a href=\"http://sourceforge.net/projects/console/\">Console
  2</a>; a slick Windows command prompt replacement.  It's lightweight, resizable,
  and with a little bit of configuration, you can make the copy-and-paste behave just
  like an xterm.\r\n\r\n"
wordpress_id: 14
wordpress_url: http://www.thedreaming.org/2011/09/06/a-better-command-prompt/
date: '2011-09-06 17:28:24 -0400'
date_gmt: '2011-09-06 22:28:24 -0400'
categories:
- Uncategorized
tags:
- Software
- DOS
- Command Line
comments: []
---
<p>If you've spent much time doing development work on Linux or Max OS X, and you suddenly find yourself stuck doing development work on a Windows machine, one of the things you'll quickly learn to hate is the Windows command prompt.  You can't resize the command prompt window, and cut-and-paste is a bit of a pain.  You can use <a href="http://x.cygwin.com/">Cygwin/X</a> to get yourself a <a href="http://www.zieg.com/faqs/cygwin/#cygwin_rxvt">genuine xterm window</a>, but Cygwin is a little heavy weight, and not all Windows console programs will work properly in Cygwin due to differences in the way POSIX handles stdout.</p>
<p>Enter <a href="http://sourceforge.net/projects/console/">Console 2</a>; a slick Windows command prompt replacement.  It's lightweight, resizable, and with a little bit of configuration, you can make the copy-and-paste behave just like an xterm.</p>
<p><a id="more"></a><a id="more-14"></a></p>
<p>Here are some configuration tips for Console 2:</p>
<p><strong>Getting rid of the clutter:</strong></p>
<ul>
<li>Right click the background of a terminal window, and choose "Edit"->"Settings".</li>
<li>Under "Appearance"->"More...", uncheck "Show menu", "Show toolbar", and "Show status bar".</li>
</ul>
<p><strong>Making Console2 Behave like XTerm For Copy-and-Paste:</strong></p>
<ul>
<li>Under "Behavior", check "Copy on select" and "Clear selection on copy"</li>
<li>Under "Hotkeys"->"Mouse", set:
<ul>
<li>"Copy/clear selection" to "None"</li>
<li>"Select text" to "Left"</li>
<li>"Paste test" to "Middle"</li>
<li>"Context menu" to "Right"</li>
</ul>
</li>
</ul>
<p>Finally, if you install <a href="http://www.microsoft.com/download/en/details.aspx?id=274">Windows Services for Unix</a>, you get commands like "ls", "which", "find", etc... to work the way you expect them to on other operating systems.  When installing SFU, you will be prompted whether you'd like to make Windows use case-sensitive file names.  Be forewarned that turning on case sensitive names in Windows can break many applications.  Also, make sure the SFU directory shows up early in your <a href="http://geekswithblogs.net/renso/archive/2009/10/21/how-to-set-the-windows-path-in-windows-7.aspx">PATH environment variable</a> (before "C:\Windows\system32"), otherwise some commands (notably "find") will be overridden by the windows versions of those commands.</p>
