---
title: Why is my node.js SSL connection failing to connect?
tags:
- nodejs ssl
date: '2016-09-27 14:17:00'
---
When an SSL connection fails in node.js, node.js usually gives you a helpful error message like "ECONNRESET" or
"unable to verify the first certificate".  These errors don't always tell you what is going wrong.  Worse, if you go
looking on stack overflow, you'll usually get helpful advice like setting `rejectUnauthorized: false` or set the
`NODE_TLS_REJECT_UNAUTHORIZED` environment variable to 0; these are terrible suggestions because the take away almost
all of the security that you're hoping to gain by using SSL in the first place.

Here is a list of interesting reasons why node.js fails to connect to an SSL server, and how to fix them.  If you
have any situations you've run into that are missing here, feel free to chime-in in the comments below.

<!--more-->

## Self Signed Certificate

One cheap way to get encryption is to use a self-signed certificate.  So long as you have some back-channel way of
getting a copy of your certificate to the client, this is actually a perfectly safe thing to do; basically, you
set up your server with the self-signed certificate, and you set up your client side to trust the self-signed
certificate and only the self-signed certificate.  In node.js, this is done with the `ca` option:

    var https = require('https');
    var fs = require('fs');    
    var certificate = fs.readFileSync('cert.pem');

    var options = {
        host: serverHost,
        port: 443,
        path: '/',
        ca: [certificate]
    };
    https.request(options, function(res) {
        res.pipe(process.stdout);
    }).end();

This should successfully connect to your server.  Note that this *only* trusts your self-certificate.  If you replace
`serverHost` with "google.com" above, your connection will fail with "UNABLE_TO_GET_ISSUER_CERT_LOCALLY".

If you're running into problems, you can try out the (more or less) equivalent with openssl directly (although this
won't actually do an HTTP request).  This can sometimes be handy for figuring out what is going wrong:

    openssl s_client -CAfile cert.pem -connect serverHost:443 < /dev/null

Fetching the certificate from the server and then doing the above at runtime is a bad idea - if someone successfully
executes a man-in-the-middle attack, or replaces the target server, then you'll be fetching a self-signed certificate
from the bad guys, but if you have a copy of the certificate ahead of time, then you're good.

## Error: Hostname/IP doesn't match certificate's altnames

When you connect to "google.com" from your webbrowser, you get back a certificate.  The certificate has a CN field
which is going to be "google.com".  This is important, because if you get back a CN from "evilbadguys.com", then you
are know that you are connecting to evilbadguys when you actually want to connect to google, and something very wrong
has happened.

But, sometimes we want to do special things, like connect to 127.0.0.1 but use a certificate where the CN
is "mysecretdomain.local".  The *easiest* way to fix this is to set the `servername` option:

    var options = {
        host: '127.0.0.1',
        servername: 'mysecretdomain.local',
        port: 443,
        path: '/',
        ca: [certificate]
    };
    https.request(options, function(res) {
        res.pipe(process.stdout);
    }).end();

You can also look at the `checkServerIdentity` option, which lets you pass in a `function(servername, cert)` function,
which should return 'undefined', or else throw an error if the servername is no good.

## Server Requires SNI

When you want to run servers for multiple different clients on a single machine, you use this idea called "virtual
hosts".  The idea is, when a browser requests something with the "host" header set to "xyz.com", we serve up a
different result than if the header is sent to "acmepaint.com".  This lets us run servers for xyz.com and acmepaint.com
on the same IP address.

For a long time, this wasn't possible with HTTPS.  HTTPS is HTTP over SSL, and long before the "host" header - which is
part of the HTTP bit - gets sent to the server, the "SSL" bit has to happen.  The first part of SSL is sending down a
certificate to the client and, as mentioned above, the CN in that certificate needs to match the hostname the
client is trying to connect to.  But until the "host" header comes, the server has no way of knowing which certificate
it needs to serve.  Chicken, meet egg.

There's an extension to SSL that solves this catch 22 called "Server Name Indication".  With SNI, the client sends
along the name of the server it would like to speak to as part of the "Client Hello".

If you specify a `servername` option, then node.js will set the SNI in the Client Hello appropriately.  If you do not
specify a `servername`, then node.js will "helpfully" set the SNI to the `host` string you provided.  The problem here
is that some servers (I'm looking at you IIS) will simply drop the connection if the Client Hello contains a domain
name they don't know about.  From node.js, this looks like a very unhelpful `ECONNRESET` error.

Again, if you want to cut node.js out of the picture, you can set up an SSL connection with SNI using openssl:

    openssl s_client -servername "acmepaint.com" -connect 127.0.0.1:443 < /dev/null

## But it works from curl!

If you need to debug a problem in node.js, and you find it's working in curl or some other application, then Wireshark
is your friend.  If your node app is running on an EC2 instance, you can install tshark and run:

    sudo tshark -i eth0 -f 'host 192.168.0.27' -w bad.pcap

where 192.168.0.27 is the host you're connecting to.  Run this, then in another window get your node.js app to do it's
thing.  Then, stop and restart tshark with "-w good.pcap" and run your curl command.  Now you can load up these pcap
files in the desktop version of Wireshark and figure out what's different between your case and the successful case.
Even if there's no successful case, Wireshark can be a handy tool to figure out where things are going wrong, just
based on who drops the connection and during what part of the SSL handshake.
