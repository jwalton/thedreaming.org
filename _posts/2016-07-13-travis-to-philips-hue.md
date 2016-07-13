---
title: Changing a Philips Hue Lightbulb when your Travis Build Fails
tags:
- aws
date: '2016-07-13 13:20:00'
---

I recently set up a Hue lightbulb in our office to show red when our Travis-CI builds are failing, and green when
they pass.  This was done with a mix of AWS Lambda and IFTTT.

<!--more-->

First of all, your Hue bridge has to be connected to your Hue account, you need a IFTTT account, and you need an AWS
account.  I'll assume you have all of that setup and running.

### Configure IFTTT

First, we head over to IFTTT and create a new recipe.  For the trigger, pick the Maker channel, and the "Receive a Web
Request" trigger.  Set the "Event Name" to "travis_webhook".  For the action, we pick "Philips Hue", and "Change color".
Pick which lights you want to change color, and in the "Color value or name" put "{{Value1}}" (which is going to take
`value1` from our POST to the Maker channel.)  This will give you a URL; keep this handy for later.

### Create Lambda Function

Now we create a new Lambda function.  So head over to AWS Lambda and click the big
"Create a Lambda function" button.  Pick "Node.js 4.3" from the dropdown of runtimes, and click "Next".  You don't need
to configure any triggers, so skip that step.  In the code box, you're going to put:

    'use strict';
    const https = require('https');
    console.log('Loading function');

    const BRANCH = "master";
    const WEBHOOK_PATH = "/trigger/travis_webhook/with/key/blahblahblah";

    exports.handler = (event, context, callback) => {
        const data = JSON.parse(decodeURIComponent(event.payload.replace(/\+/g,  " ")));
        console.log('Received event:', JSON.stringify(data, null, 2));

        if(data.branch !== BRANCH) {
            // Ignore non-master commits
            return callback(null, "Nothing to do...");
        }

        const color = (data.status_message === 'Passed') ? 'green' : 'red';

        console.log("Setting light color to " + color);

        const postData = JSON.stringify({value1: color});

        const req = https.request({
                hostname: 'maker.ifttt.com',
                port: '443',
                path: WEBHOOK_PATH,
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Content-Length': Buffer.byteLength(postData)
                }
            },
            (res) => {
                let body = '';
                res.setEncoding('utf8');
                res.on('data', (chunk) => body += chunk);
                res.on('end', () => {
                    console.log('Successfully processed HTTPS response: ' + body);
                    callback(null, "Reply from IFTTT: " + body);
                });
            }
        );
        req.on('error', callback);
        req.write(postData);
        req.end();

    };

Set the `WEBHOOK_PATH` variable to the path that IFTTT gave you for your new recipe.

### Set up the API Gateway

Now, we run into a slight problem - You may have noticed that rather strange
`decodeURIComponent(event.payload.replace(/\+/g,  " "))` above.  Travis (rather strangely) sends JSON data inside a
x-www-form-urlencoded blob.  AWS doesn't support x-www-form-urlencoded requests, so we need to deal with that, and
we'll do it with [these instructions](https://forums.aws.amazon.com/thread.jspa?messageID=663593&tstart=0#663593)
(which I'll post here for posterity, and because the screens have changed a little):

Head on over to the Amazon API gateway, and pick "Create API".  Make sure "New API" is picked at the top, and enter a
name for your API (something like "Travis to Hub Webhook").

* Click on "Actions" and then "Create Method" (you might want to "Create Resouce" and make a "/travis_webhook"
resource, and then create your "Method" under that.  One way you end up posting to some big URL, the other you
post to a big URL that ends in "/travis_webhook").
* Pick "Post" from the dropdown and click the checkmark.
* Pick "Lambda Function" as your "Integration type", pick a region, and then type the name of your lambda function from
  above. Click "Save".
* Click on "Integration Request".
* Expand "Body Mapping Templates".
* Under "Contet-Type", click "Add mapping template".  Set the content-type to "application/x-www-form-urlencoded", and
  click the checkmark.  (If prompted, click "No, use current settings" when it complains about securing the
  integration.)
* In the textbox on the right, enter this blob of text:

        ## convert HTTP POST data to JSON for insertion directly into a Lambda function

        ## first we we set up our variable that holds the tokenised key value pairs
        #set($httpPost = $input.path('$').split("&"))

        ## next we set up our loop inside the output structure
        {
        #foreach( $kvPair in $httpPost )
         ## now we tokenise each key value pair using "="
         #set($kvTokenised = $kvPair.split("="))
         ## finally we output the JSON for this pair and add a "," if this isn't the last pair
         "$kvTokenised[0]" : "$kvTokenised[1]"#if( $foreach.hasNext ),#end
        #end
        }

* Click "Actions" -> "Deploy API".  Create a new stage named "prod".  This will give you an "Invoke URL".  Copy this
  down, because we're going to need it when we...

### Configure Travis-CI.com

In your .travis.yml file, add this block:

    notifications:
      webhooks:
        urls:
          - https://invoke-url-goes-here

Filling in the URL.

Push that, and your light should change whenever your build happens.  Note that IFTTT is a bit slow about pushing
changes to Hue, so it can take a few seconds for the light to actually change.

Hope that was helpful.  Enjoy!
