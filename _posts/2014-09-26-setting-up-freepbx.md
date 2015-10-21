---
title: "Setting up FreePBX"
tags:
- asterisk
- freepbx
- pbx
---

I'm setting up a FreePBX system for my house.  My goal is to make it so that I can make and receive calls using a phone in the house.

When someone calls in, they are greeted with a voice menu (IVR in FreePBX terms) which simply asks them to press 1 to talk to a human.  This is done to screen out telemarketers - most telemarketers dial your house by robot, and then connect a human to the other end of the line once you pick up and say "Hello."  This is usually not an instant process, which is why you usually have to say "hello" a few times.  Therefore, the telemarketers usually miss the IVR, and are greeted with silence.

<!--more-->

Right now I'm using a SPA-3102 both as an ATA (to turn the phones in my house into SIP phones) and as a trunk (to turn the local "public switched telephone network" or PSTN into a SIP device I can route calls to.)  With a setup like this it is trivial to route some or all of your calls over a VoIP service, if you're looking to save some money on your phone bill.

Installing FreePBX
==================

I created a Virtual Machine using VirtualBox to run the PBX.  Since this is a small PBX just for my house, we don't have much in the way of computational requirements; 768MB of RAM will suffice (I think you could probably make this work with 512MB, but you'll see the RAM usage creep up into the 90% range...)

The first step is to [install the FreePBX distro](http://wiki.freepbx.org/display/FD/Installing+FreePBX+Official+Distro) on our VM.  This tutorial was written using 5.211.65-17.

The current version of FreePBX comes with a tool called iSymphony.  This is a for-pay plugin which we don't need, and it takes up a lot of RAM, so the first thing we'll do is disable this.  From *Admin -> Module Admin*, click on "iSymphonyV3" and check "Uninstall", then scroll to the bottom and click "Process".  This will uninstall the module from FreePBX, but will still leave the iSymphony service running in the background.  ssh to your FreePBX box as root and run:

    sudo service iSymphonyServerV3 stop
    sudo mv /etc/init.d/iSymphonyServerV3 ~

I also like to set my hostname.  Edit /etc/sysconfig/network, and set `HOSTNAME=pbx`.  Edit /etc/hosts and add `pbx` to the list of domains that resolve to `127.0.0.1` and `::1`.  You can also run `hostname pbx` to change the hostname immediately, without requiring a reboot.

While we're logged in as root, now is a good time to [change the Asterisk admin password](http://www.freepbx.org/support/documentation/faq/changing-the-asterisk-manager-password.)  Go to *Settings -> Advanced Settings* and change the *Asterisk Manager Password*, then click the green checkbox next to the field to change it.

Configuring the SPA-3102 as a Client
====================================
Login to your SPA-3102 as administrator, and go to the "Advanced" settings.  In the Line 1 tab:
Under "Proxy and Registration" set:

* Proxy and Registration -> Proxy: Set this to the IP address of your FreePBX machine.
* Subscriber Information
  * Display Name: [Set to whatever you like]
  * User ID: "6000" - This is the extension we'll create in FreePBX for our phones.
  * Password: [Your secret password here]

Then we need to add an extension to FreePBX.  Go to *Applications -> Extensions*.  Add a new "Generic SIP Device".

    User Extension: 6000
    Display Name: House Phones
    CID Num Alias: [Your phone number, with no spaces or dashes - I'll use 6135551234 as an example.]
    Outbound CID: "Jason Walton" <6135551234>

    Device Options:
    secret: [Password from SPA-3102]

    Voicemail:
    Status: Enabled
    Voicemail Password: [Your numeric voicemail password here]
    Email Address: [Your email address here]

Configuring the SPA-3102 as a Trunk
===================================
To setup the SPA-3102 and FreePBX, I basically followed the instructions I found [here](http://www.freepbx.org/support/documentation/howtos/howto-linksys-spa-3102-sipura-spa-3000-freepbx).

If you don't want to configure a DID, set Dial Plan 2 to "S0<:s>", and then set PSTN Caller Default DP to "2".  In FreePBX, when you create an Inbound Route, set the "DID Number" to "s".  This makes it so when someone calls, the SPA3102 will redirect our call to FreePBX.

Making sure the SPA-3102 is Working
===================================

If you go to the "Info" tab on the SPA-3102, look for "Registration State"; this should be "Registered" (note there's one for "Line 1 Status" and a different one for "PSTN Line Status".)  If it isn't "Registered", you've got something wrong.  The "Next Registration In" line will tell you when the SPA-3102 next plans to try to register.  This number will be bigger with each failed registration.

A Second Trunk
==============

I'm using voip.ms as a cheap way to route my long distance, so I followed the [instructions here](http://wiki.voip.ms/article/FreePBX_/_PBX_in_a_Flash_(SIP)) to setup a second trunk.  As of this writing, the screen shots are based on a slightly older version of FreePBX, but they'll get you up and running.  You should be able to set up almost any VoIP provider as a trunk.  If you set up an *Outbound Caller ID* (e.g. "<6135551234>") then voip.ms will use this as your caller ID, so you can make it look like calls are coming from your land line.

Outbound Routes
===============

Outbound routes are calling patterns that determine how an outbound call will be routed.  When someone dials a number from a phone inside your house, it will match one of the outbound routes, which will determine which outbound trunk will be used.  Setting up different patterns lets you do things like route local calls over your PSTN while routing long distance calls over a cheaper VoIP provider or even over Google Hangouts.

Under *Connectivity -> Outbound Routes*, we're going to configure a bunch of routes.  For each, you need to set a "Route Name" (which can't have spaces) and one or more Dial Patterns.  The dial patterns below go in the "match pattern" box.

We have 10 digit dialing here in Ottawa, so I configured the following routes:

    local:
        Match Pattern:
            613XXXXXXX
            343XXXXXXX
            819XXXXXXX
            873XXXXXXX
        Trunk Sequence: 0: "SPA 3102"

    emergency:
        Match Pattern:
            911
        Trunk Sequence: 0: "SPA 3102"

    longdistance:
        Match Pattern:
            1NXXNXXXXXX
        Trunk Sequence: 0: "voipms"

Note here we're using voip.ms to route long distance calls instead of over the SPA 3102 by setting this to be your trunk provider.

Once you have outbound routes set up, you should be able to plug in a phone and make some calls!

Setting Up the IVR
==================
Go to *Admin -> System Recordings*.  Here is where you can record messages for playback in the IVR.  You can either upload files, if you already have something recorded, or you can record messages here:

* Enter your extension into the top box (6000) and hit "Go".
* Pick up your phone, dial "*77".  At the beep, record your message ("Please press 1 to speak to a human.").  Press "#" when finished.
* Back on the web page, enter a name for the recording ("PressOneForHuman") and click "Save".

Now go to *Applications -> IVR*.  Click "Add a new IVR".

    IVR Name: Welcome
    Announcement: PressOneForHuman
    Timeout: 60
    Invalid Retry Recording: None
    Invalid Recording: None
    Invalid Destination: Terminate Call: Hangup
    Timeout Retries: Disabled

    IVR Entries:
    Ext: 1, Destination: Extensions -> 6000

Finally, go to *Connectivity -> Inbound Routes* (or go edit the Inbound Route you created while setting up the SPA-3102 above, if you created one.)  Click "Add Incoming Route".

    Description: [Your phone number]
    DID Number: "s"
    Set Destination: "IVR" -> "Welcome"

Testing our IVR
===============

Go to *Applications -> Extensions*.
Add a new "None (virtual exten)" extension.

    User Extension: 7000
    Display Name: IVR
    Ring Time: 1
    No Answer: IVR -> Welcome

Pick up your phone and dial "7000#".  You should be connected to your IVR.  If you press "1" you should hear a call waiting beep (since you're on the phone, calling yourself.)  Assuming you don't answer the call waiting beep, you should eventually be forwarded to voicemail.  Note that the voicemail greeting will tell you "The person at extension six zero zero zero is unavailble...".  So, next we want to set up voicemail.

A quick aside here; why "7000#" instead of just "7000"?  7000 will work, but you'll notice you have to wait a while before you're connected.  This is because FreePBX is unsure if you're going to dial more digits or not - you might still match some outbound route.  Usually you solve this sort of thing on a PBX by having all your outbound routes have a "9" prefix or similar, so you dial 9 to get out; this means that anything that doesn't start with a 9 must be an extension, and FreePBX can route your calls faster.  Since we're setting this up for a home setting, where we only have one extension, we're not going to be dialing other extensions often, and no one expects to have to dial 9 to get out of your house, so we don't bother.  Here, when we actually do want to dial an extension, the "#" tells FreePBX that we're done dialing, and not to wait for more digits.

Set up Voicemail
================

By default, all you need to do is dial "*97" to get to your mailbox.  You an also dial "*98" to get into a mailbox for another extension.

To record a greeting, dial *97, enter your password, and then press "0" to get to "Mailbox Options".  From here, press "1" to record you "Unavailable Message" (played when you don't answer), "2" to record your "Busy Message" (played when you're on the phone), and "3" to record your name.

Google Voice and Skype
======================

<p><strike>If you're interested in getting outbound calling working through Google Hangouts, check out <a href="http://sites.psu.edu/psuvoip/2010/11/09/adding-google-voice-to-freepbx/">this article</a>.  I've successfully had this running with a plain Google Talk account in Canada, without Google Voice, although it sounds like this sort of thing is now <a href="https://plus.google.com/u/0/+NikhylSinghal/posts/MjyncJEbzxK">officially frowned upon by Google</a>.  Too bad, as this was a good way to get free long distance.</strike></p>

Update: chan_gtalk and res_jabber have been replaced in Asterisk 11 with chan_motif an res_xmpp.  Go to *Admin -> Module Admin*.  Under "Repositories" make sure "Basic", "Extended", and "Unsupported" are all highlighted.  Click "Check Online".  You should see a module called "Google Voice/Chan Motif".  I haven't had a chance to play with this yet, but [this](http://highsecurity.blogspot.ca/2012/12/asterisk-11-and-chanmotif-on-freepbx.html) will likely be helpful reading.

I haven't tried setting up Skype, but you might be able to get Skype working by [following these instructions](http://www.freepbx.org/support/documentation/howtos/how-to-set-up-a-skype-gateway).


311
===

Here in Ottawa, if you dial 311 from a local phone, it sends your call to the City of Ottawa offices.  We'd like this to work.

There's two ways to set this up.  If you're using a VoIP provider like voip.ms, we can set up an outbound route for this.  Go to *Connectivity -> Outbound Routes* and create a new route.  Name the route "services", and create a Dial Pattern as follows:

    prepend: 6135802400
    prefix: 311
    math pattern: leave this blank

Whenever a call is placed, FreePBX will try to match the call against a `prefix+pattern`.  If if finds a match, it will strip the `prefix` from the number dialed, and prepend the `prepend`.  In effect, this makes it so when you dial `311`, you're actually dialling 613-580-2400, which is the City of OTtawa.

Alternatively, if you have a real PSTN line plugged into your SPA-3102, you can set this up in the Dial Plan on the SPA-3102 directly.  In the "Line 1" tab, under Dial Plan, use something like:

    (*xx|*21*xx.|#21#|[3469]11<:@gw0>|0|00|613[2-9]xxxxxx|343[2-9]xxxxxx|819[2-9]xxxxxx|873[2-9]xxxxxx|1xxx[2-9]xxxxxxS0|xxxxxxxxxxxx.)

The "<@:gw0>" will route calls to 311, 411, 611, and 911 through to to PSTN, bypassing FreePBX completely.  You can read more about SPA-3102 dial plans [here](http://voicent.com/predictive-dialer/blog/index.php/predictive-dialer/380/spa3102-dial-plan) and [here](http://www.cisco.com/c/en/us/support/docs/collaboration-endpoints/spa901-1-line-ip-phone/108747-pqa-108747.html).

Note that if you use a dial plan like this for 911, you have to be double-plus-sure you deconfigure this if you ever switch from using a PSTN to a Voip line, otherwise 911 won't work for you.

Update: Setting up gmail as your email server
=============================================

These days most ISPs will block you from sending email over the SMTP port, so you need to use an intermediary like gmail to send email for you.  This is [stolen from Steve McCann's blog](http://www.stevemccann.net/2012/12/changing-freepbx-smtp-server-to-gmail.html), so go read that if you want all the details, but basically you want to SSH into your FreePBX machine, add the following lines to /etc/postfix/main.cf:

    relayhost = [smtp.gmail.com]:587
    smtp_sasl_auth_enable = yes
    smtp_sasl_password_maps = hash:/etc/postfix/sasl_passwd
    smtp_sasl_security_options = noanonymous
    smtp_use_tls = yes

Then create /etc/postfix/sasl_passwd (replacing your username and password as appropriate):

    [smtp.gmail.com]:587 user.name@gmail.com:password

And finally run the following commands:

    chmod 400 /etc/postfix/sasl_passwd
    postmap /etc/postfix/sasl_passwd
    chown postfix /etc/postfix/sasl_passwd
    /etc/init.d/postfix reload

