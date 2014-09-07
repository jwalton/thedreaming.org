---
layout: post
status: publish
published: true
title: Reason and VMPK on Windows 7 64-bit
author: Jason Walton
excerpt: "A friend of mine wanted to get Reason up and running on his laptop, so he
  could mix up some mad beats on an airplane.  It's a bit tough to lug a MIDI keyboard
  about on the plane with you, though.  You might learn to play a more <a href=\"http://usa.yamaha.com/products/music-production/midi-controllers/wx5/?mode=model\">compact
  MIDI instrument</a>, but a better solution is to use a \"virtual instrument\".\r\n\r\n"
wordpress_id: 15
wordpress_url: http://www.thedreaming.org/2012/03/05/reason-and-vmpk-on-windows-7-64-bit/
date: '2012-03-05 21:15:13 -0500'
date_gmt: '2012-03-06 02:15:13 -0500'
categories:
- Uncategorized
tags:
- Reason
- MIDI
- Windows 7
- Music
comments: []
---
<p>A friend of mine wanted to get Reason up and running on his laptop, so he could mix up some mad beats on an airplane.  It's a bit tough to lug a MIDI keyboard about on the plane with you, though.  You might learn to play a more <a href="http://usa.yamaha.com/products/music-production/midi-controllers/wx5/?mode=model">compact MIDI instrument</a>, but a better solution is to use a "virtual instrument".</p>
<p><a id="more"></a><a id="more-15"></a></p>
<p>Enter <a href="http://vmpk.sourceforge.net/">Virtual MIDI Piano Keyboard</a>, or VMPK, a free virtual MIDI keyboard.  Here's what you need to do to get this set up:</p>
<ul>
<li>Download <a href="http://nerds.de/en/download.html">LoopBe1</a>.  This is a "virtual MIDI port" - it gives you a fake port to plug your fake keyboard into, and a fake device to read MIDI data from in Reason.  It's free for non-commercial use.</li>
<li>Install and run LoopBe1.  You should see a little black MIDI port in your system tray.</li>
<li>Install and run <a href="http://vmpk.sourceforge.net/">VMPK</a>.</li>
<li>In VMPK, go "Edit"->"Connections".  Set "Output MIDI Connection" to "LoopBe Internal MIDI".</li>
<li>In Reason, go "Edit"->"Preferences".  Set the "Page" dropdown to "Keyboards and Control Surfaces".</li>
<li>Click "Add".</li>
<li>Pick the following:
<ul>
<li>Manufacturer: &lt;Other&gt;</li>
<li>Model: MIDI Control Keyboard</li>
<li>MIDI Input: LoopBe Internal MIDI</li>
</ul>
</li>
<li>Click "OK" and then close Prefernces.</li>
</ul>
<p>Now you can bang out tunes on your virtual keyboard.  Enjoy!</p>
