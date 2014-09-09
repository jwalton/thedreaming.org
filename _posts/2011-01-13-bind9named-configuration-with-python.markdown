---
layout: post
status: publish
published: true
title: Python Library for Bind9/named Configuration
wordpress_id: 12
wordpress_url: http://www.thedreaming.org/2011/01/13/bind9named-configuration-with-python/
date: '2011-01-13 21:54:52 -0500'
date_gmt: '2011-01-14 02:54:52 -0500'
tags:
- bind9
- bind
- DNS
- named
- Python
- library
comments: []
---
I had to spend some time this week generating a Bind9 configuration file from a database.  I decided to learn Python at the same time.  :)  This is a quick [Python module]({{ site.baseurl }}/files/Bind9Tools.py) that will let you build Bind9 config files in no time flat:

<!--more-->

{% highlight python %}
import Bind9Tools
hosts = [
    Bind9Tools.Host("thedreaming.org.",
         ["192.168.0.1", "209.217.122.208"],
         aliases = ["www", "ftp", "mail", "tachikoma"],
         mailExchangers = [Bind9Tools.MailExchanger("thedreaming.org.")]),
    Bind9Tools.Host("lucid", ["192.168.0.10"], ipv6Addresses = ["fe80::0224:01ff:fe0f:7770"]),
    Bind9Tools.Host("mystic", ["192.168.0.11"]),
    Bind9Tools.Host("renegade.thedreaming.org.", ["192.168.0.12"]),
    Bind9Tools.Host("www.renegade", ["192.168.0.13"])
]

zone = Bind9Tools.Zone("thedreaming.org.", "root.thedreaming.org", ["thedreaming.org."], hosts)

zoneFile = open('db.thedreaming.org', 'w')
zone.writeZoneFile(zoneFile)
zoneFile.close()

zoneFile = open('db.192.168.0', 'w')
zone.writeReverseZoneFile(zoneFile, "192.168.0.")
zoneFile.close()

zoneFile = open('db.f.e.8.0.0.0.0.0.0.0.0.0.0.0.0.0', 'w')
zone.writeReverseIPv6ZoneFile(sys.stdout, "f.e.8.0.0.0.0.0.0.0.0.0.0.0.0.0.")
zoneFile.close()
{% endhighlight %}

If you find this useful, or have suggestions for improvements, drop me a line in the comments!
