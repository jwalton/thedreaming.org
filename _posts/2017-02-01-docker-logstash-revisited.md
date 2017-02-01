---
title: "Setting up Logstash with Docker Revisited"
tags:
- docker
- logstash
- elasticsearch
- kibana
---
This is an updated version of [this post](/2014/11/21/docker-logstash/).  This is a quick and easy way to get
Elasticsearch, Logstash, and Kibana up and running in Docker.
<!--more-->

## ELK

Logstash is typically run with an [Elasticsearch](http://www.elasticsearch.org/) backend to store log files, and [Kibana](http://www.elasticsearch.org/overview/kibana/) as a front end for querying logs and building dashboards.
These three are run together so often that together they are called the "ELK" stack.

## Running in Docker

The following will start a new Elasticsearch, Logstash, and Kibana server in a "docker network" named "elk":

    mkdir -p ~/docker/logstash
    cat > ~/docker/logstash/logstash.conf <<EOL
    input {
      tcp {
        port => "9998"
        codec => json
      }
    }
    output {
      elasticsearch {
        hosts => "elasticsearch"
      }
    }
    EOL
    docker network create elk
    docker run -it -d --net elk --name elasticsearch -p 9200:9200 -p 9300:9300 elasticsearch:latest
    docker run -it -d --net elk --name logstash -p 9998:9998 -v ~/docker/logstash.conf:/config-dir logstash:latest -f /config-dir/logstash.conf
    docker run -it -d --net elk --name kibana -e ELASTICSEARCH_URL=http://elasticsearch:9200 -p 5601:5601 kibana:latest

The first bit creates a new logstash.conf file.  Obviously you can tweak this to suit your needs.  The four docker
commands at the bottom create the network, and run all the bits of the ELK stack.  Since we're using a dedicated
network, the various docker containers can find each other by name instead of doing any "--link"ing.  This is
considerably less fragile.
