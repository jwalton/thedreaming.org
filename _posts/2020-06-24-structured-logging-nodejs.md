---
title: "Structured logging in Node.js with Winston and Elasticsearch"
tags:
  - node.js
  - winston
  - logging
  - elasticsearch
---

This article is going to explore using [winston](https://github.com/winstonjs/winston)
and [Elasticsearch](https://github.com/elastic/elasticsearch) to do
"structured logging" in Node.js.  The basic idea is that we want to write logs
with some metadata attached to them, beyond just a timestamp, a level, and a message.

The traditional "twelve factors" approach to logging is just to write your logs
to stdout, and let some extrenal process deal with logging.  For example, you
might use fluentd to read stdout on all your processes and write the results
into Elasticsearch.  This works well, and it works across different projects
written in different languages.  But, with a little extra work, we can write
some extra information into those logs.

For example, for every request we could write the URL of the request to the log
as `request.url`, and then write the response time in milliseconds as
`response.responseTime`, and now it's a simple mater to generate an
Elasticsearch graph showing our average and max response time to HTTP requests,
or even to write a query which finds the top ten slowest routes in our system.
Or we could write a `user` field to the log on every request, so we can figure
out which users in our system are most active.

<!--more-->

## Structured logging with Winston

We're going to use winston as the heart of our logging engine.  Firsts, let's
play around a little with winston so you can get a quick idea of what we can do:

```js
import winston from 'winston';
const logger = winston.createLogger();

logger.log({level: 'info', message: 'Hello world!'});
```

And if you try running this, you'll get:

```sh
[winston] Attempt to write logs with no transports {"level":"info","message":"Hello world!"}
```

Ok, that didn't go so well.  What's all this about transports?

Basically, you can think of winston as a stream; you write logs into it, and it
streams out log events to one or more "transports".  In fact, Transport
[just extends `stream.Writable`](https://github.com/winstonjs/winston-transport/blob/master/index.d.ts#L11).
Let's add a console transport so we can see logs on stdout:

```js
import winston from 'winston';
const logger = winston.createLogger({
    transports: [
        new winston.transports.Console({}),
    ]
});

logger.log({level: 'info', message: 'Hello world!'});
```

And now we get:

```sh
{"level":"info","message":"Hello world!"}
```

This is a little bit better, but we're still looking at a raw JSON event.  In
additon to "transports", winston has this concept called a "format".  You can add
a format (or multiple formats via `winston.format.combine()`) to a transport.
Each format will receive a copy of each event before it's passed to the transport,
and can modify fields, or even add or remove fields.  Let's add some formats
to our logger to print out pretty messages to the console:

```js
import winston from 'winston';
import debugFormat from 'winston-format-debug';
const logger = winston.createLogger({
    transports: [
        new winston.transports.Console({
            format: winston.format.combine(
                winston.format.colorize({ message: true }),
                debugFormat({
                    colorizeMessage: false, // Already colored by `winston.format.colorize`.
                })
            )
        }),
    ]
});

logger.log({level: 'info', message: 'Hello world!'});
```

If you run this, you'll get:

```sh
Jun 24 14:27:38 node[94522] INFO:    Hello world!
```

So now we have something "human readable".

We've already seen that we can add a "message" and a "level" to a log event.
What else can we add? It turns out we can add whatever we like. If we try:

```js
logger.log({level: 'info', message: 'Hello world!', test: 'This is a test'});
```

This will output:

```sh
Jun 24 14:29:18 node[94522] ERROR:   Hello world!
    test: "This is a test"
```

We can add any literally any fields we want here. It's up to the format and the
transport to decide what to do with those fields.  Formats can also modify fields.
You could write, for example a [format to prefix all the "tags" in an event onto "message"](https://github.com/jwalton/node-jwalton-logger/blob/master/src/logging/format/prefixFormat.ts)
to show them in stdout, or a [format to replace a `request` object with a pretty-printed string](https://github.com/jwalton/node-jwalton-logger/blob/master/src/logging/format/requestFormat.ts).

## From Winston to Elasticsearch

To get our logs out to elasticsearch, we need to do a few things.  First, we
need to decide exactly what fields we want to store in elasticsearch, and write
a template for our index.  This helps Elasticsearch figure out what type each
value in our log entry is.  Also we set `number_of_shards: 1` here - these are
just logs, so there's no real need to duplicate these across multiple shards or
replicas.  Also, Elasticsearch generates an index for every field in every message,
so we want to limit what we send to Elasticsearch to something "well defined" to
stop our memory usage from spiraling out of control.

```ts
// elasticsearchTemplate.ts
export default {
    index_patterns: 'log-*',
    settings: {
        number_of_shards: 1,
        number_of_replicas: 0,
        index: {
            refresh_interval: '5s',
        },
    },
    mappings: {
        _source: { enabled: true },
        properties: {
            '@timestamp': { type: 'date' },
            message: { type: 'text' },
            tags: { type: 'keyword' },
            err: { type: 'text' },
            level: { type: 'keyword' },
            name: { type: 'keyword' },
            'src.file': { type: 'keyword' },
            'request.method': { type: 'keyword' },
            'request.url': { type: 'keyword' },
            'request.normalizedUrl': { type: 'keyword' },
            'request.remoteAddress': { type: 'keyword' },
            'response.statusCode': { type: 'short' },
            'response.responseTime': { type: 'float' },
            'response.fullHeaders': { type: 'text' },
        },
    },
};
```

Then we can create a "format" which will take in an object with a `request`, and
a `response`, and will format them according to this template:

```ts
// esFormat.ts
import * as http from 'http';
import ld from 'lodash';
import os from 'os';

const HOSTNAME = os.hostname();

interface EsInfo {
    '@timestamp': string;
    message: string;
    pid: number;
    host: string;
    tags?: string[];
    err?: string;
    level?: string;
    name?: string;
    request?: {
        method: string;
        url: string;
        normalizedUrl: string;
        remoteAddress: string;
    };
    response?: {
        statusCode: number;
        responseTime: number;
        fullHeaders: string;
    };
}

/**
 * Format messages before sending them to elasticsearch.
 */
export class EsFormat {
    transform(info: any): any {
        const result: EsInfo = {
            '@timestamp': info['@timestamp'] || new Date().toISOString(),
            host: HOSTNAME,
            message: info.message || '',
            pid: process.pid,
            tags: info.tags,
            err: info.err ? info.err.stack() : undefined,
            level: info.level,
            name: info.name,
        };

        const { request, response } = info;
        if (request) {
            result.request = {
                method: request.method || '',
                url: (request as any).originalUrl || request.url,
                normalizedUrl: normalizeExpressPath(request),
                remoteAddress: (request as any).ip,
            };
        }
        if (response) {
            result.response = {
                statusCode: response.statusCode,
                responseTime: (response as any).responseTime, // Need to add this yourself,
                fullHeaders: JSON.stringify(
                    ld.omit(response.getHeaders(), 'set-cookie', 'server-timing')
                ),
            };
        }

        return result;
    }
}

export default function() {
    return new EsFormat();
}

/**
 * Given an express request, returns the normalized URL of the request.
 *
 * The basic idea here is when someone visits
 * "/api/v2/User/5ddc3ed8643713eb372b993a", we want to collect metrics about
 * the endpoint "/api/v2/User/:id".  This works for Exegesis paths, too.
 *
 */
function normalizeExpressPath(req: http.IncomingMessage) {
    const expressReq = req as any;
    if ('route' in expressReq && expressReq.route.path !== undefined) {
        return (expressReq.baseUrl || '') + expressReq.route.path.toString();
    } else {
        return undefined;
    }
}
```

Finally we can create an elasticsearch transport to add to our logger, to
actually get our logs to elasticsearch.

```ts
import { LogData, ElasticsearchTransport } from 'winston-elasticsearch';
import elasticsearchTemplate from './elasticsearchTemplate';
import esFormat from './format/esFormat';

// Set ELASTICSEARCH_URLS to a list of URLs to connect to, e.g. "http://elasticsearch:9200".
const { ELASTICSEARCH_URLS } = process.env;

if (ELASTICSEARCH_URLS) {
    const nodes = ELASTICSEARCH_URLS.split(',');

    // winston-elasticsearch automatically moves a bunch of the log data into
    // a field called "meta".  This undoes this and moves it all back...
    function esTransformer({ message, level, timestamp, meta }: LogData) {
        return { message, level, timestamp, ...meta };
    }

    const esTransport = new ElasticsearchTransport({
        transformer: esTransformer,
        clientOpts: { nodes } as any,
        indexPrefix: 'log',
        mappingTemplate: elasticsearchTemplate,
        ensureMappingTemplate: true,
        format: esFormat(),
    });

    logger.add(esTransport);
}
```

And now anything we log will be automatically sent to elasticsearch, in full
structured glory.

## Caveats

One thing be aware of with this approach.  Notice if you do something like:

```ts
logger.log({level: 'error', message: 'Ohs noes!', err});
process.exit(1);
```

Here there's no chance for the elasticsearch transport to send a network request
to elasticsearch before you `process.exit(1)`, so your error log is not going
to go anywhere.  You can get around this by using the `callback` form of `logger.log`:

```ts
logger.log({level: 'error', message: 'Ohs noes!', err}, () => {
    process.exit(1);
});
```

But, also, if your node.js process crashes beacuse of an uncaught
exception or because it runs out of memory, it will print an error to stderr and
then die, and again, this won't make it to elasticsearch.  For this reason, in a
produciton environment it's a good idea to write your structured logs out to
elasticsearch, but also capture stdout and stderr with something like fluentd.

## Full example with code

If you want to see a more fully-fleshed out example, check out
[this example on github](https://github.com/jwalton/jwalton-logger).  You can
clone this repo and run `docker-compose up` to bring up a web app on port 3000
which logs to a Kibana instance on [http://localhost:5601](http://localhost:5601).
When you first launch Kibana, click "Connect to your Elasticsearch index", set
the "Index pattern" to "log-*", and use "@timestamp" as the time fitler.  Then
click on the hamburger menu in the upper left corner and go to the "Discover"
tab to see your logs.

This project does exactly what's described in this blog post, but also adds a
`Logger` class which makes it so things passed into the log are type safe, and
removes any "extra" properties passed in so they don't accidentally get passed
on to Elasticsearch.
