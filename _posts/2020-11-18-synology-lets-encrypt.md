---
title: "Setting up HTTPS on a Synology with Let's Encrypt and Route 53"
tags:
  - DNS
  - Synology
  - Crypto
---

The Synology now comes with a built in "Let's Encrypt" client, but unforunately it only supports HTTP-01 challenge, which means if you want to use it you need to open up your Synology to the Internet.  The Internet is a scary place, so we're going to use the DNS-01 challenge to validate we own our domain name.

<!--more-->

## Register a Domain

We need to register a domain name, so this will cost some money annually.  To generate a certificate with Let's Encrypt, you need to "prove" you own the domain name.  Usually you use an app like Certbot or Lego to do this proof for you, but it either boils down to serving a randomly generated string from your web server from a specific path, or placing that randomly generated string in a TXT DNS record.  To do the first, we'd have to open a hole in our firewall, and we don't want to do that.  To do the second, we'll have to use an API to talk to our DNS provider.  My preferred DNS provider has an API, but it's in beta and you have to jump through some hoops to get access, so let's do this with Amazon's AWS.

So start off by going to AWS's "Route 53" and registering a domain name.  Let's say you get "example.com" - we'll use this as our example domain name all through this article, but you'll need to replace this with whatever domain name you register.  Once you register it, go to the "Hosted Zones" section on the left, pick your domain, and click "Create Record".  Choose "Simple Routing" and then click "Define simple record".  Set the record name to "synology.example.com".  Under "ValueRoute traffic to" pick "IP Address or another value depending on the record type".  In the box below that, enter your synology's IP address (e.g. 192.168.0.10).  Click "Define Simple Record" then "Create records".  This creates what is called an "A Record" (short for "address record") for "synology.example.com".  Then, find something else to do for a bit, because it can take a while for this to propagate.  You can check if it's done by running `nslookup synology.example.com` from your terminal until you get back an answer.

## IAM User

We want to create a new IAM policy and IAM user - we don't want to use our "root" user's credentials in AWS, because we're going to have to store these credentials on the synology, and if someone gets access to our synology we don't want them to take over our entire AWS account.  First, go to Route 53 again, click on ["Hosted zones"](https://console.aws.amazon.com/route53/v2/hostedzones#) and take note of the "Hosted Zone ID" for the domain in question.  Now head over to IAM, click on "Policies" on the left, and then "Create policy".  Switch to the JSON tab, and copy paste the following (update your domain name in the ID and replace "YOUR-ZONE-ID-HERE" with your actual zone ID):

```json
{
    "Version": "2012-10-17",
    "Id": "lets encrypt - example.com",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "route53:ListHostedZones",
                "route53:ListHostedZonesByName"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
               "route53:GetChange",
               "route53:ChangeResourceRecordSets",
               "route53:ListResourceRecordSets"
            ],
            "Resource": [
                "arn:aws:route53:::hostedzone/YOUR-ZONE-ID-HERE",
                "arn:aws:route53:::change/*"
            ]
        }
    ]
}
```

Click "Review policy", then give you policy a name (like "lets_encrypt_example.com"), and click "Create policy".  Now click on the "Users" tab on the left, click "Add user", give the user a name (again I used "lets_encrypt_example.com") and check the checkbox for "Programmatic access".  Click "Next" and then click on the "Attack existing policies directly" tab, and select the policy you just created from the list (it's easiest if you search for it by name).  Copy the "Access Key ID" and "Secret Access Key", and keep them somewhere safe.  We'll need them in a minute.  Make sure you protect these!  These are like a password for this user.

## Setup the Synology

The Synology has an nginx instance listening on port 80 and port 443.  There's no way to easily disable this nginx service from the GUI.  But we can use this nginx service ourselves.  If our goal is just to provide HTTPS access to the Synology UI (and perhaps to other services running on the Synology), then basically, we're going to generate a certificate, copy it overtop of the Synology's nginx certificate, and then restart the nginx server, and do this automatically whenever the certificate needs to be renewed.

If, on the other hand, our goal is to expose some services running on the Synology in Docker to the public internet, we might be better off setting up something like a Traefik reverse proxy running on some port other than 443, and then we can use our router's port forwarding feature to forward external traffic to that port.  This makes it easier to prevent anyone from getting to the Synology admin interface.  This guide doesn't cover this option, but there are lots of good guides out there about how to do this.

## Enable SSH Access

We're going to do some tinkering in the command prompt (technically you could do the whole Traefik thing via the Docker UI on the Synology, but it'll be easier via SSH).  To do this, open the "Control Panel", pick "Terminal & SNMP", then check "Enable SSH service" and click "Apply".

## Install lego

We're going to install [`lego`](https://github.com/go-acme/lego), a go-based implementation of the ACME protocol for talking to Let's Encrypt:

```sh
wget https://github.com/go-acme/lego/releases/download/v4.1.0/lego_v4.1.0_linux_$(dpkg --print-architecture).tar.gz
tar xvzf lego_v4.1.0_linux_$(dpkg --print-architecture).tar.gz lego
sudo mkdir -p /usr/local/sbin
sudo mv ./lego /usr/local/sbin
sudo chown root:root /usr/local/sbin/lego
# Make sure it works!
./lego --version
```

At this point, we're ready to give this a try and generate a certificate.  We'll create certificates as the root user, and store them somewhere other users on the system can't get access to them.  Run:

```sh
# Become root
sudo su -
mkdir letsencrypt
chmod 700 letsencrypt
cd letsencrypt
```

Inside this new `letsencrypt` folder, create a file called config.sh.  Replace these variables
as required:

```sh
# config.sh
export AWS_ACCESS_KEY_ID=REPLACE_ME
export AWS_SECRET_ACCESS_KEY=REPLACE_ME
export LE_DOMAIN="example.com"
export LE_EMAIL_ADDRESS="your@email.address"
```

And then create a second file called `lego-create.sh`:

```sh
#!/usr/bin/env bash
# lego-create.sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

# Can't use default key-type ec256 with Synology.
lego --key-type rsa4096 --accept-tos \
  --dns="route53" \
  --email="${LE_EMAIL_ADDRESS}" \
  --domains="${LE_DOMAIN}" \
  --domains="*.${LE_DOMAIN}" \
   run
```

Then give it a run:

```sh
chmod 700 ./lego-create.sh
./lego-create.sh
```

This can take several minutes, so if it looks like it's hung, just wait a little bit.  When this is done, it will write a few files to ./.lego/certificates/example.com.*.

### Add Certificates to Synology

If this worked, then now we have some certificates!  We need to get the Synology to use them.  The Synology stores certificates in `/usr/syno/etc/certificate/_archive/`.  Each certificate in this folder is stored with a seemingly random name.  There's an `INFO` file here in JSON format which we might be able to edit directly, but instead let's import our certificates via the GUI.

Download the certificates you just created to your local machine.  Go to the "Control Panel", pick "Security", and then pick the "Certificate" tab and click "Add".  Choose "Add a new certificate", then add a description (e.g. "example.com") and click next, then upload the certificates you generated; the ".key" for for the "Private Key", the ".crt" file for the "Certificate", and the ".issuer.crt" file for the "Intermediate certificate".  Then click on the "Configure" button, and set your new ceritifcate to be the system default and the FTPS certificate.  Left click on your new certificate, then right click and pick "Edit" from the context menu, and then check "Set as default certificate" (if you skip this step, you'll have to come back here and configure any new services you create to use the certificate).

If all is successful, you should now be able to visit `https://synology.example.com:5001/` without any security warnings.

### Automatic renewals

We have certificates installed, but if you look in the Synology GUI, you'll see they expire in about three months.  We need to automate fetching new certificates from Let's Encrypt, copying them into the Synology's folder, and then restarting the nginx server.

Run the following, still as root:

```sh
cat /usr/syno/etc/certificate/_archive/INFO
```

And you should get some output like this:

```json
{
   "QlWeCZ" : {
      "desc" : "",
      "services" : []
   },
   "xoEBak" : {
      "desc" : "example.com",
      "services" : [...]
   },
}
```

The "xoEBak" section with "example.com" in it is the Synology identifier for our ceritificate.  Let's add this to our config.sh file:

```sh
# config.sh
# ...
export SYNOLOGY_CERT_ID="xoEBak" # Replace this
```

Create a new script to install certificates in /root/letsencrypt called "installcerts.sh":

```sh
#!/usr/bin/env bash
# installcerts.sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${DIR}/config.sh"
LEGO_FOLDER="${DIR}/.lego/certificates"
SYNOLOGY_FOLDER="/usr/syno/etc/certificate/_archive/${SYNOLOGY_CERT_ID}"

# Copy certificates
cp ${LEGO_FOLDER}/${LE_DOMAIN}.crt ${SYNOLOGY_FOLDER}/cert.pem
cp ${LEGO_FOLDER}/${LE_DOMAIN}.issuer.crt ${SYNOLOGY_FOLDER}/chain.pem
cat ${LEGO_FOLDER}/${LE_DOMAIN}.crt ${LEGO_FOLDER}/${LE_DOMAIN}.issuer.crt > ${SYNOLOGY_FOLDER}/fullchain.pem
cp ${LEGO_FOLDER}/${LE_DOMAIN}.key ${SYNOLOGY_FOLDER}/privkey.pem

# Restart the Synology nginx server
/usr/syno/etc/rc.sysv/nginx.sh reload
```

And then, create another new script to renew certificates, "lego-renew.sh".  This will only renew certificates if they expire in the next 20 days, and will run "installcerts.sh" only if the certificates were renewed:

```sh
#!/usr/bin/env bash
# lego-renew.sh
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
source "${DIR}/config.sh"

# Can't use default key-type ec256 with Synology.
lego --key-type rsa4096 --accept-tos \
  --dns="route53" \
  --email="${LE_EMAIL_ADDRESS}" \
  --domains="${LE_DOMAIN}" \
  --domains="*.${LE_DOMAIN}" \
   renew --days 20 --renew-hook="${DIR}/installcerts.sh"
```

Let's test out our renew script and our installcerts script:

```sh
$ chmod 700 ./*.sh
$ ./lego-renew.sh
2020/11/18 15:30:58 [example.com] The certificate expires in 89 days, the number
of days defined to perform the renewal is 20: no renewal.
$ ./installcerts.sh
alias-register stop/waiting
```

Finally, we need to automate renewal.  In the Synology UI, go to "Control Panel", "Task Scheduler", click "Create" => "Scheduled Task" => "User Defined Script".  Set the task name to "Renew LE Certs", make sure the "User" is "root".  Under the "Task Settings" tab, set the "User-defined script" to "/root/letsencrypt/lego-renew.sh".  Check the "Send run details by email" box, enter your email address, and check "Send run details only when the script terminates", and then click "OK".

### Finishing up

Under "Control Panel" => "Network", in the "DSM Settings" tab, check "Automatically redirect HTTP connection to HTTPs for DSM desktop.  This will make it so if you go to `http://synology.example.com:5000`, it will redirect you to `https://synology.example.com:5001`.

If you want to access the DSM via port 443, under "Domain" on the same page, check "Enable customized domain", and set the value to "synology.example.com".  Now you can login to the synology via `https://synology.example.com` directly.  (Note if you do this that you will not be able to access it via `https://synology.example.com:5001`).

If you have other services running on the Synology, you can make it so you can access them by domain name.  If you have a [Navidrome](https://www.navidrome.org/) instance running on port 4533, for example, you could add a new A Record in Route 53 for "navidrome.example.com" pointing it at the IP of your synology, and then in "Control Panel" => "Application Portal", under the "Reverse Proxy" tab, click "Create".  Under source, set the "Protocol" to "HTTPS", the "Hostname" to "navidrome.example.com", and the "Port" to "443".  In the "Destination" set "Protocol" to "HTTP", "Hostname" to "localhost", and set the "Port" to "4533".  Now you should be able to visit `https://navidrome.example.com` and it will take you straight to the navidrom interface.
