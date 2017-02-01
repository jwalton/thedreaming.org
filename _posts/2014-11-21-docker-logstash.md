---
title: "Setting up Logstash with Docker"
tags:
- docker
- logstash
- elasticsearch
- kibana
---
Because this took me all day today, I wanted to share how to get [Logstash](http://logstash.net/)
up and running under [Docker](https://www.docker.com/).

<!--more-->

**There's an updated version of this post [here](/2017/02/01/docker-logstash-revisited/).**

## ELK

Logstash is typically run with an [Elasticsearch](http://www.elasticsearch.org/) backend to store log files, and [Kibana](http://www.elasticsearch.org/overview/kibana/) as a front end for querying logs and building dashboards.  These three are run together so often that together they are called the "ELK" stack.

Every version of Logstash has a "recommended" version of Elasticsearch, and can run an "embedded" Elasticsearch server.  For the latest Logstash at the time of this writing (v1.4.2) this is Elasticsearch v1.1.1.  This is a pretty old version of Elasticsearch, and it has some nasty bugs, so one of the things we're going to do later on is run our own Elasticsearch in it's own container, which is where this starts to get... exciting.

In my examples here I'm also going to setup the TCP input plugin for logstash, so that
I can log from my node.js app with [Bunyan](https://github.com/trentm/node-bunyan) and
[bunyan-logstash-tcp](https://github.com/chris-rock/bunyan-logstash-tcp) (more on this further
down.)  You could also easily use UDP and [bunyan-logstash](https://www.npmjs.org/package/bunyan-logstash).

## The Very Quick and Easy Way

So, the very quick way to get this all running is to use the embedded version, and if this is
"good enough for you", then this is how you do it.  First, create your "logstash-embedded.conf"
file, which should look like:

    input {
      tcp {
        'port' => "9998"
        codec => json
      }

      udp {
        'port' => "9999"
        codec => json
      }
    }

    output {
      elasticsearch {
        embedded => true
      }
    }


Then we're going to use P. Barrett Little's [docker-logstash](https://github.com/pblittle/docker-logstash) image to get things going:

    docker run -d \
      --name logstash \
      -p 9292:9292 \
      -p 9200:9200 \
      -p 9998:9998 \
      -p 9999:9999/udp \
      -v /path/to/logstash-embedded.conf:/opt/logstash.conf \
      pblittle/docker-logstash

We expose port 9292 because this is the port Kibana is running on.  We also have to expose port
9200 because this is the port for Elasticsearch, and Kibana's web client needs access to it.
Finally we expose port 9998 so that we can log to this Logstash instance from our Bunyan logger.
We can optionally specify something like `-v /mnt/elasticsearch/data:/data` to mount a local
folder as a data volume to store our Elasticsearch database in.

## The More Complicated and Insecure Way

If you run into the limitations of Elasticsearch v1.1.1, you can run Logstash with a more recent
version of Elasticsearch.  To do this, we're going to have to run Elasticsearch and Kibana in
their own containers.

First of all, our updated "logstash.conf" file which tells logstash to forward data to Elasticsearch running on the "es" machine on port 9300:

    input {
      tcp {
        'port' => "9998"
        codec => json
      }
    }

    output {
      elasticsearch {
        host => es
        port => 9300
      }
    }

Then, we run the following commands:

    # Elasticsearch:
    docker run -d -p 9200:9200 -p 9300:9300 --name elasticsearch \
      dockerfile/elasticsearch \
      /elasticsearch/bin/elasticsearch \
      -Des.http.cors.enabled=true

    # Kibana
    docker run -d \
      --name kibana \
      -e ES_HOST="\"+window.location.hostname+\"" -e ES_PORT=9200 \
      -p 9292:80 \
      arcus/kibana

    # Logstash:
    docker run -d \
      --name logstash \
      --link elasticsearch:es \
      -p 9998:9998 \
      -p 9999:9999/udp \
      -v /Users/jwalton/logstash.conf:/opt/logstash.conf \
      pblittle/docker-logstash

Note the `-Des.http.cors.enabled=true` flag we pass to Elasticsearch - this is needed to get
Elasticsearch 1.4.x+ working with Kibana.  Kibana will try to fetch data from Elasticsearch,
but Kibana and Elasticsearch are on different ports, so from JavaScript's perspective, they
are different origins and thus run afoul of the same origin policy.  This option makes
Elasticsearch send an `Access-Control-Allow-Origin` header, which tells your browser to let
Kibana do it's thing.  Elasticsearch sent these by default in 1.3 and older.

## With Basic Authentication and SSL

Suppose we're putting our Kibana server out there on the Internet - we probably want to control who has access to Kibana with a username and password (and since Kibana needs access to Elasticsearch, this means we need to setup basic auth for Elasticsearch, too.)  To get this setup, we're going to take a page right out of the [Elasticsearch docs](http://www.elasticsearch.org/blog/playing-http-tricks-nginx/) and front Elasticsearch and Kibana with nginx.  (Note that the Kibana container is actually running nginx to serve Kibana, so we're putting nginx in front of nginx...  We could probably do this more efficiently, but this works.)

First, we're going to create a docker data volume container to store our nginx configuration:

    docker run -d --name nginx-conf -v /etc/nginx nginx echo "nginx config"

Running the `nginx` image will also create the default nginx config for us.

First lets create a self-signed certificate and a password file in our nginx-conf volume:

    docker run -it --rm --volumes-from nginx-conf ubuntu bash
    $ apt-get update
    $ apt-get install openssl
    $ mkdir /etc/nginx/ssl
    $ cd /etc/nginx/ssl
    $ openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt
    $ cd ..
    $ apt-get install apache2-utils
    $ htpasswd -c /etc/nginx/kibana.htpasswd username
    $ mkdir /etc/nginx/sites-enabled


Now we create `kibana.conf` (adapted from [this version](http://tom.meinlschmidt.org/2014/05/19/securing-kibana-elasticsearch/)):

    server {
        # we listen on :8080
        # listen       8080;

        # SSL
        listen       8080 ssl;
        server_name  somer.server;
        ssl_certificate      /etc/nginx/ssl/nginx.crt;
        ssl_certificate_key  /etc/nginx/ssl/nginx.key;

        ssl_session_cache shared:SSL:1m;
        ssl_session_timeout  5m;

        ssl_ciphers  HIGH:!aNULL:!MD5;
        ssl_prefer_server_ciphers   on;

        charset utf-8;

        # root for Kibana installation
        location / {
            auth_basic "Restricted";
            auth_basic_user_file /etc/nginx/kibana.htpasswd;

            proxy_http_version 1.1;
            proxy_set_header  X-Real-IP  $remote_addr;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  Host $http_host;
            proxy_pass http://kibana:80;
        }

        # and for elasticsearch
        location /es {
            auth_basic "Restricted - ES";
            auth_basic_user_file /etc/nginx/kibana.htpasswd;

            rewrite ^/es/_aliases$ /_aliases break;
            rewrite ^/es/_nodes$ /_nodes break;
            rewrite ^/es/(.*/_search)$ /$1 break;
            rewrite ^/es/(.*/_mapping)$ /$1 break;
            rewrite ^/es/(.*/_aliases)$ /$1 break;
            rewrite ^/es/(kibana-int/.*)$ /$1 break;
            return 403;

            proxy_http_version 1.1;
            proxy_set_header  X-Real-IP  $remote_addr;
            proxy_set_header  X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header  Host $http_host;
            proxy_pass http://es:9200;
        }

    }

Finally, let's copy our config to the data volume container:

    docker run --rm -it --volumes-from nginx-conf -v ~:/home ubuntu bash
    cp /home/kibana.conf /etc/nginx/conf.d/

Note the above works even if you're using boot2docker on OS/X, because boot2docker will
automatically map the /Users folder on your OS/X machine into the boot2docker VM.

Now we can start up all of this with:

    # Elasticsearch:
    docker run -d -p 9300:9300 --name elasticsearch \
      dockerfile/elasticsearch \
      /elasticsearch/bin/elasticsearch

    # Kibana
    docker run -d \
      --name kibana \
      -e ES_SCHEME="https" -e ES_HOST="\"+window.location.hostname+\"" -e ES_PORT="8080/es" \
      arcus/kibana

    # Logstash:
    docker run -d \
      --name logstash \
      --link elasticsearch:es \
      -p 9998:9998 \
      -p 9999:9999/udp \
      -v /Users/jwalton/logstash.conf:/opt/logstash.conf \
      pblittle/docker-logstash

    # nginx:
    docker run -d \
      --name nginx \
      --link elasticsearch:es \
      --link kibana:kibana \
      -p 8080:8080 \
      --volumes-from nginx-conf \
      nginx

Note the horrific abuse of `arcus/kibana`'s `ES_PORT` field to get Kibana to look for elasticsearch at our non-standard `/es` URL.  Also notice we no longer need to set `http.cors.enabled` on Elasticsearch, since Elasticsearch and Kibana are now being served from the same port.

## Logging with Bunyan

Here's a quick example of logging straight to logstash with Bunyan:

    var bunyan      = require('bunyan');
    var bunyanTcp   = require('bunyan-logstash-tcp');

    var log = bunyan.createLogger({
        name: 'myLogger',
        serializers: bunyan.stdSerializers,
        streams: [
            {
                level: 'debug',
                type: 'raw',
                stream: (bunyanTcp.createStream({
                    host: '192.168.59.103',
                    port: 9998,
                    max_connect_retries: -1, // Don't give up on reconnecting
                    retry_interval: 1000     // Wait 1s between reconnect attempts
                }))
            }
    });

    log.info("Hello world");

Note we specify a `max_connect_retries` and `retry_interval`.  By default, bunyan-logstash-tcp
will use a retry inteval of 100ms, and will only try to reconnect 4 times (which means if your
logstash instance is down for 400ms, you will stop sending it logs.)  The `max_connect_retries: -1`
makes it so we'll keep trying forever.

## I'm Not Seeing Any Logs in Kibana

If you aren't seeing your logs, the first thing to do is to go to http://hostname:9200/_aliases?pretty (or https://hostname:8080/es/_aliases?pretty, if you're using the SSL/basic auth version.)  This will list all the indexes in your Elasticsearch database.  You should see some "logstash-YYYY.MM.DD" entries for today.

If you see some entries, but the date is wrong, and you're on boot2docker, note that boot2docker has an annoying bug on OS/X where if you sleep your machine, the clock will stop advancing on the boot2docker VM while your machine is asleep.  You can fix the time on the VM by running:

    $ boot2docker ssh
    $ sudo date -s '2014-11-20 13:00:00'

(Use the current time instead of November 20th, obviously.)  If you don't see any entries, then check to see if logstash is actually getting any data.  Add this to the output section of your logstash config:

      stdout {
        codec => rubydebug
      }

then `docker rm -f logstash`, restart your logstash container, and run `docker logs -f logstash` - any logs that logstash is seeing it should show up in stdout.
