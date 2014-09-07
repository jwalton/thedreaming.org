---
layout: post
status: publish
published: true
title: Creating an SPF record
author: Jason Walton
wordpress_id: 16
wordpress_url: http://www.thedreaming.org/2012/08/21/creating-an-spf-record/
date: '2012-08-21 16:58:21 -0400'
date_gmt: '2012-08-21 21:58:21 -0400'
categories:
- DNS
tags:
- DNS
- SPF
---
So, you want to add an SPF record to your domain.

First, SPF records used to be held in TXT records, but more modern DNS systems hold the SPF data in an actual "SPF" record.  If your DNS solution doesn't support SPF, then use the TXT record instead.  Either way, the format is the same.  Here's a very simple example, which only allows mail sent from an IP address listed in one of the MX records for the domain example.com:

    example.com.  IN SPF "v=spf1 +mx -all"

<!--more-->

The bit in quotes is the actual record: "v=spf1 +mx -all".  What does this mean?  The `v=spf1` is required, and defines this as an SPF1 record.

The rest of this is a set of conditions to match, in left-to-right order.  The first matching condition will determine the outcome of the SPF rule.  Each condition here consists of a "qualifier" ("+" or "-", here) followed by a "mechanism" ("mx", "all"):

* `+mx` is a condition that says "Go lookup the MX records for this domain.  If the sender is from one of those IP addresses, then pass."
* `-all` is a condition that says "Match everything, and fail."

Some handy mechanisms:

* `mx` - Matches if the sender's IP matches an MX record for the domain.
* `a` - Matches if the sender's IP matches an A record for the domain.
* `include:someotherdomain.com` - Run the SPF rules for another domain, and match if it passed.

And this is the set of all modifiers:

* `+` - Pass.  This is the default, if no modifier is specified.
* `-` - Fail.  The client will get an error message saying that it is not authorized to send mail for the domain.
* `!` - SoftFail.  This is something better than a "Fail", but worse than a "Neutral".  The server won't reject a message based on this alone, but might reject the message if it fails some other check (a high spam score, for example.)
* `?` - Neutral.  This means the server should treat the message as if there was no SPF record.

Here's another handy example:

    example.com.  IN SPF "v=spf1 mx a include:_spf.google.com ~all"

This will let anyone send a message from an @example.com email address if the message comes from an IP address from one of the MX records, or from one of the A records, or if it is being sent from a google.com mail server (handy if you want to let your users send mail from GMail or Google Apps.)  If none of these conditions are true, then the message will "softfail" - Google recommends using "~all" instead of "-all" because the set of IP addresses they send mail from changes regularly.

If you want more details on SPF, have a look at [HOWTO - Define an SPF Record](http://www.zytrax.com/books/dns/ch9/spf.html), or read the [RFC](http://www.ietf.org/rfc/rfc4408.txt).
