---
layout: post
status: publish
published: true
title: A Layman's Guide to Deep Packet Inspection
excerpt: "<h2>What is Deep Packet Inspection?</h2>\r\n\r\nSuppose you send a postcard
  to someone.  On the left hand side of the post card, you write your return address,
  you write the address you want the card to be delivered to, and hopefully you remember
  to add some stamps.  On the right hand side, you fill in the message you want to
  send (\"Hey mom!  Wish you were here!\").  Then you drop your postcard into a mailbox.
  \ Your postcard will be picked up by a mail carrier, and go through a sorting process.
  \ Postal workers will look at the destination address to decide where to send the
  postcard, and it will move from postal center to postal center until eventually
  it arrives in the hands of a postman who delivers it right to the door of your intended
  recipient.\r\n\r\nThis is similar to the way the Internet works.  Instead of using
  postcards, the Internet works by sending data in \"packets\".  A packet has a \"header\"
  which has some information about what computer the packet is from and what computer
  or server the packet is going to, and a body which contains the actual message that
  is being sent (\"Hey mom!  Wish you were here!\").  When your computer sends a packet
  out into the Internet, it is passed through a series of \"routers\"; each router
  reads the address of the computer the packet is destined for from the header, and
  either passes it on to another router, or else passes it on to the destination computer.\r\n\r\nOr
  at least, that is how it has worked up until very recently.  Routers have been getting
  smarter, and modern routers use a technology called \r\n\"Deep Packet Inspection\",
  or \"DPI\", to decide what to do with their packets.\r\n\r\nWhen you send a postcard,
  you expect it to be delivered based on what your write on the left hand side, but
  suppose for a minute that postal workers also read the right hand side of your card,
  and used that information to decide how to handle its delivery.  For example, the
  post office might decide to give priority to messages it thought were important;
  if there are too many postcards to deliver in a day, your \"Hi mom!\" message might
  have to wait until tomorrow so that a postcard could be delivered today that said
  \"Patient at our hospital needs a new heart.  Send transplant right away!\"  Or,
  a somewhat more nefarious use; the post office might decide to simply not deliver
  any postcards that said something bad about the post office.  Or what if the post
  office decided to start keeping a database of all the businesses you sent and received
  postcards to and from, so that they could sell this information to advertisers?\r\n\r\nThis
  is exactly what DPI is all about; DPI enabled routers will route packets based not
  only on the header of the packet, but also based on the content of the message,
  and may use the contents of those messages for other purposes as well.\r\n\r\n"
wordpress_id: 11
wordpress_url: http://www.thedreaming.org/2009/06/06/a-laymans-guide-to-deep-packet-inspection/
date: '2009-06-06 09:39:52 -0400'
date_gmt: '2009-06-06 14:39:52 -0400'
categories:
- Software
tags:
- DPI
- Deep Packet Inspection
- Traffic Shaping
- QoS
- ISP
- Internet
comments:
- id: 150
  author: JJ
  author_email: john_l_jarvis@hotmail.com
  author_url: http://johnljarvis.blogspot.com/
  date: '2010-04-27 15:58:30 -0400'
  date_gmt: '2010-04-27 20:58:30 -0400'
  content: "Hey Jason, great post. I didn't know about those BT trials; crazy...\r\n\r\nJJ"
- id: 160
  author: Verizon FIOS Discounts
  author_email: ''
  author_url: http://www.fx-deals.com/fios/verizon-fios-discounts/
  date: '2011-02-04 05:15:26 -0500'
  date_gmt: '2011-02-04 10:15:26 -0500'
  content: |-
    <strong>Verizon FIOS Discounts...</strong>

    thedreaming.org " Blog Archive " A Layman's Guide to Deep ... Verizon FIOS Discounts Friday...
- id: 213
  author: "レイバン ショップ"
  author_email: gfykrib@gmail.com
  author_url: http://www.sealinfant.info/
  date: '2013-09-09 19:30:21 -0400'
  date_gmt: '2013-09-10 00:30:21 -0400'
  content: "プレイボーイ ダウン"
- id: 242
  author: Angeline
  author_email: ''
  author_url: http://www.nitzankagan.com/guests_book/msg/298.html
  date: '2014-06-23 08:08:46 -0400'
  date_gmt: '2014-06-23 13:08:46 -0400'
  content: "<strong>Angeline...</strong>\n\nthedreaming.org » Blog Archive » A Layman\x92s
    Guide to Deep Packet Inspection..."
- id: 293
  author: Kelly
  author_email: kellybonner@hotmail.com
  author_url: http://datingcoach.cc
  date: '2014-08-30 13:47:27 -0400'
  date_gmt: '2014-08-30 18:47:27 -0400'
  content: "Hi! This is my first visit to your blog! We are a collection of volunteers
    and starting a new initiative in a community in the same niche.\r\nYour blog provided
    us beneficial information to work on. You have done a extraordinary job!"
---
<h2>What is Deep Packet Inspection?</h2>
<p>Suppose you send a postcard to someone.  On the left hand side of the post card, you write your return address, you write the address you want the card to be delivered to, and hopefully you remember to add some stamps.  On the right hand side, you fill in the message you want to send ("Hey mom!  Wish you were here!").  Then you drop your postcard into a mailbox.  Your postcard will be picked up by a mail carrier, and go through a sorting process.  Postal workers will look at the destination address to decide where to send the postcard, and it will move from postal center to postal center until eventually it arrives in the hands of a postman who delivers it right to the door of your intended recipient.</p>
<p>This is similar to the way the Internet works.  Instead of using postcards, the Internet works by sending data in "packets".  A packet has a "header" which has some information about what computer the packet is from and what computer or server the packet is going to, and a body which contains the actual message that is being sent ("Hey mom!  Wish you were here!").  When your computer sends a packet out into the Internet, it is passed through a series of "routers"; each router reads the address of the computer the packet is destined for from the header, and either passes it on to another router, or else passes it on to the destination computer.</p>
<p>Or at least, that is how it has worked up until very recently.  Routers have been getting smarter, and modern routers use a technology called<br />
"Deep Packet Inspection", or "DPI", to decide what to do with their packets.</p>
<p>When you send a postcard, you expect it to be delivered based on what your write on the left hand side, but suppose for a minute that postal workers also read the right hand side of your card, and used that information to decide how to handle its delivery.  For example, the post office might decide to give priority to messages it thought were important; if there are too many postcards to deliver in a day, your "Hi mom!" message might have to wait until tomorrow so that a postcard could be delivered today that said "Patient at our hospital needs a new heart.  Send transplant right away!"  Or, a somewhat more nefarious use; the post office might decide to simply not deliver any postcards that said something bad about the post office.  Or what if the post office decided to start keeping a database of all the businesses you sent and received postcards to and from, so that they could sell this information to advertisers?</p>
<p>This is exactly what DPI is all about; DPI enabled routers will route packets based not only on the header of the packet, but also based on the content of the message, and may use the contents of those messages for other purposes as well.</p>
<p><a id="more"></a><a id="more-11"></a></p>
<h2>Good Uses of DPI</h2>
<p>DPI is a technology that has the potential to do many interesting things.  Like any technology, DPI is neither inherently good or evil, although like any technology it can be used for both good and evil things.  The "heart transplant" example above is one example of "good DPI"; most people wouldn't mind too much if their "Hi Mom!" postcard was delayed by a day if it meant someone's life could be saved.  This application is known as "Quality of Service" or QoS; the router in this case is giving a higher Quality of Service to postcards from hospitals.</p>
<p>If the postcard example seems a bit contrived, then consider the case of medical telepresence;  This is a technology which allows a doctor in one city to perform an operation on someone in another city remotely.  This allows allows remote locations, where it is hard to get access to specialist doctors, a much better quality of medical care.  Today these sorts of operations are rarely done over the Internet, and more frequently done over much more expensive leased-line networks.  This is exactly because the Internet cannot deliver the QoS guarantees required to do this sort of delicate work.  You might think it is a pain when YouTube pauses for a few seconds while buffering video, but imagine if that were to happen while you were using the video to try and operate on someone (or imagine if it happened while someone was operating on you!)  DPI could be used to give priority to medical telepresence connections over much cheaper Internet connections, and both make this technology much more affordable, and bring it to many more remote communities.</p>
<p>Another technology, very similar to QoS, is called "traffic shaping"; if you have a home Internet router, used to share your Internet connection between multiple computers, it might well do some simple form of traffic shaping.  It might, for example, prioritize your Skype traffic over your BitTorrent traffic;  Most people would rather have a clear voice call and have their downloads take a bit longer than have a choppy distorted voice call and have their downloads be a little bit faster.  As soon as you hang up your Skype call, there are no more Skype packets to route, and BitTorrent traffic returns to full speed.  This techonology makes it so you don't have to manually pause your BitTorrent client just to make a phone call, and it would be impossible to do without DPI.</p>
<p>DPI can also be used to stop the spread of virii and other malicious software.  The "<a href="http://en.wikipedia.org/wiki/Code_Red_worm" target="_blank">Code Red</a>" computer worm was an increadibly successful worm which attacked untold numbers of computers in 2001, through an exploit found in Microsoft's IIS Web Server.  Estimates for the amount of damage caused by Code Red vary, but most agree that it was in the billions.  Code Red, however, had a very distinctive "signature" to the messages it sent to try and infect other computers; DPI could have been used to very effectively halt the spread of Code Red.</p>
<h2>Evil Uses of DPI</h2>
<p>DPI is also a technology with much potential for abuse, and the "evil" uses of DPI are the ones most people are probably more familiar with, as they more often make it into the news.</p>
<p>As hinted at in our postcard analogy, DPI can be used to disrupt communication that your ISP doesn't approve of.  Your Internet service provider might use DPI to try and disable or degrade the quality of VoIP services, such as Skype or Vonage.  Your ISP could then charge you a premium to use these services, or might offer their own VoIP service which isn't so encumbered.  This can give a large ISP an artificial advantage when new and innovative services are rolled out, and prevents smaller companies from being able to compete.  This ultimately makes it less likely for small companies to innovate.</p>
<p>When a given ISP degrades or disrupts a given service, it is also confusing and annoying for customers, who might find a service they use works very well from home, but not at all from work or from a friend's house.  There is also something a bit sleazy about a company which intentionally damages a service they are offering you, and then asks you to pay to "fix" that service; it feels a bit like the customer is being asked to pay protection money.</p>
<p>Here in Canada, it has become popular for ISPs to use DPI to limit the speed of (or "throttle") file-sharing services, such as BitTorrent.  For a long time the many smaller DSL based ISPs were not throttling their connections, however when Bell Canada started to loose customers to these smaller ISPs, Bell used DPI to throttle their competitors; something they can do because they control the "last mile" infrastructure.  Bell has effectively been given the ability to eliminate any means a smaller ISP might use to differentiate their service from Bell's own.</p>
<p>DPI can also be used to analyze the traffic you send and receive, to analyze what web sites you visit and services you use, in order to do targeted advertising.  This exact application has been <a href="http://en.wikipedia.org/wiki/Phorm#BT_trials" target="_blank">trialed by British Telecom</a>.  Wireless carriers in Canada have been using similar technologies to strip out and <a href="http://www.michaelgeist.ca/content/view/3734/159/" target="_blank">replace advertising</a> from online services.  This allows the wireless carrier to essentially steal the advertising revenue of the web sites their users visit.</p>
<h2>Privacy Concerns</h2>
<p>Some of these applications, like targeted advertising and customer tracking, are highly invasive and raise obvious privacy concerns.  In some ways the privacy concern may seem overblown.  The "postcard" analogy is a good one here; when you send a postcard, you probably don't care if a postman reads your postcard.  If you don't trust your postman, you would use an envelope instead of a postcard.  The closest equivalent to an envelope on the Internet is encryption, and using encryption does foil some applications of DPI.</p>
<p>However encryption often only solves half the problem; while your ISP may no longer know exactly what you are reading or talking about, it is usually still possible to determine where an encrypted connection is going, and therefore the ISP can infer what services you are using.  Encryption also remains uncommon, except in situations where it is obviously required such as in applications like online banking or e-commerce.  Also, many consumers are unsure how to tell if their communications over the Internet are encrypted, and in many cases it would not be obvious how to make them so.</p>
<p>Another example of where encryption fails the consumer is the case of Rogers Cable in Canada, which uses DPI to throttle BitTorrent traffic.  When Rogers users turned to encryption to try and prevent Rogers from detecting their BitTorrent traffic, Rogers simply started throttling <a href="http://torrentfreak.com/rogers-fighting-bittorrent-by-throttling-all-encrypted-transfers/" target="_blank">all encrypted traffic</a> as well. </p>
<h2>Avoiding the Evil Uses of DPI, While Keeping the Good</h2>
<p>In truth it's difficult to see how any legislation could be passed that would allow all the good uses of DPI while similarly prohibiting the bad ones.  Forcing carriers to be transparent about how they use DPI, and about what services they throttle would certainly be a step in the right direction, but, as Kyle Rosenthal pointed out at <a href="http://www.ustream.tv/recorded/1605091" target="_blank">CFP '09</a>, in many places people have a choice of only one or two service providers so forcing the service providers to announce that they abuse their customers doesn't really help.  The market forces that ought to be fixing these problem cannot help when carriers have a monopoly or duopoly.</p>
<p>One solution to these "evil" uses of DPI is "Network Neutrality" legislation.  The idea behind Network Neutrality is that the network carrier should not treat traffic from one user or service or application any differently from any other traffic.  Network Neutrality obviously has some downsides, as many of the "good" DPI examples, such as QoS for medical uses, cannot be implemented in a truly neutral network.</p>
<p>Another possible solution might be to legislate that a service provider only be allowed to apply DPI technologies to customers which consent to them.  This solution is harder to implement than you might think.  Some DPI technologies, such as QoS applications, are typically implemented not on a per-customer level, but on an entire network level.  It is impossible to give priority to medical applications without taking away bandwidth from other applications.  It would be difficult to make this work well in a network without consent from all users.</p>
