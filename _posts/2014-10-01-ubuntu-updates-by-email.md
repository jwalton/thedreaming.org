---
title: "Automatic Notifications of Updates in Ubuntu"
tags:
- ubuntu
---
Have a server running Ubuntu?  Want an email when there are packages that need updating?  Here's how.

<!--more-->

There's a tool available to do this called "Apticron".

```
sudo apt-get update
sudo apt-get install apticron
```

After installing, edit `/etc/apticron/apticron.conf`, set the `EMAIL` variable at the top of the file, and you're done.
