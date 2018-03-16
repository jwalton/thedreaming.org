---
title: "Using Swagger/OpenAPI 2.0 in Node.js"
tags:
- javascript
- babel
- es6
- modules
- swagger
- OpenAPI
---

OpenAPI is a specification that lets you write a document which describes a
REST API.  From this document, you can generate documentation, generate stubs
to call into your API in a variety of languages, and automatically validate
requests on the server, and much more.  Swagger is a set of tools that work
with OpenAPI.  This will walk through setting up an OpenAPI document for a
typical MongoDB/Express/Node.js app.

This is the first of a three part series.

<!--more-->

## Swagger Libraries for Node.js

The state of Swagger/OpenAPI in Node.js is a bit of a mess.  First, you'll
probably notice that the [OpenAPI 3.0 spec](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md)
has been released, but as of this writing no Node.js tools support it.  The most
popular tool-chain for implementing your Swagger API server side is
[swagger-tools](https://github.com/apigee-127/swagger-tools), however this project
has officially been [deprecated](https://github.com/apigee-127/swagger-tools/issues/335)
in favor of [sway](https://github.com/apigee-127/sway) and
[sway-connect](https://github.com/whitlockjc/sway-connect).  sway-connect has
only had five commits, and the most recent of those was two years ago.  So far
no versions of sway-connect have been published on npm.

sway hasn't seen a release in 2 years either, although it forms the basis of
[swagger-node-runner](https://github.com/theganyo/swagger-node-runner).  This is
the project that's being pushed by [swagger.io](swagger.io).  There's a CLI tool
called [swagger](https://www.npmjs.com/package/swagger) which will generate
a project for you (although the project it generates is using a sadly out of date
version of swagger-node-runner).

So for this article, we're going to use swagger-node-runner directly, and ignore
the `swagger` npm project.  Note that if you're not using express,
swagger-node-runner also has support for many other popular frameworks,
including connect, hapi, restify, and sails.

## Babel Project

The code for this entire project is [available on github](https://github.com/jwalton/node-swagger-template).
The version for this specific article is [this commit](https://github.com/jwalton/node-swagger-template/tree/d2d9f6e1d326f1e227acae818b9ccdd231592f3a),
but you can check out the latest master if you're the kind of person who likes
to skip to the end of a good book.  ;)

There are lots of different ways to set up a project using Babel.  Our project
is going to have a fairly simple .babelrc using "babel-preset-env" to compile
everything to be compatible with Node.js v4.x and up.  If you're using Node.js
v8.x or higher, you should edit the .babelrc to compile to your version, as
this will leave async functions alone, which makes stepping through the code in
a debugger much more pleasant.  Also note on older versions of node.js,
babel-polyfill is required, but it can be removed on Node.js v8.x or higher.

We store our source files in /src, and the babel compiled versions end up in
/lib.

I like to run my unit tests directly from the /src folder, using `babel-register`
to compile source files on the fly.  This means you don't need to rebuild your
whole project to run a test.  This requires a little care when configuring
swagger-node-runner, as we need to tell it to load controllers from /src during
tests, but /lib in production.  The sample project does it by
["lying" to swagger-node-runner about the root folder of the app](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js#L10),
claiming to be running from the /src or /lib folder depending on which folder
`config.js` is being loaded from.

## Our Swagger API

We're going to start with a really simple API.  We want to send a request like
this one:

```
http://localhost:10010/api/v1/user?id=54f0be26ae8aba260b8f6db7
```

and we want to get back a `User` object from MongoDB.  (We're not actually
going to have a MongoDB instance in the background, as we're just interested
in the Swagger part of this.)  Our swagger definition can be found
[here](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/api/swagger/swagger.yaml).

The interesting part for now is the '/user' path:

```yaml
paths:
  /user:
    # This will be handled by src/api/controllers/user.js
    x-swagger-router-controller: user
    get:
      description: Gets a User.
      # This will be handled by the `getUser()` funciton in src/api/controllers/user.js.
      operationId: getUser
      parameters:
        - name: id
          in: query
          description: The ID of the user to get.
          required: true
          type: string
          format: ObjectId
```

The `x-swagger-router-controller` tells swagger-node-runner which source file
the "controller" for this path is in.

You'll also note that we've specified there is one required parameter "id",
which is a "string" in "ObjectId" format.  MongoDB uses 24 digit hex numbers as
IDs.  If you're familiar with OpenAPI, you'll know that "ObjectId" is not one
of the standard formats provided by OpenAPI.  We're going to do some custom
validation here; more on that in our next article.

Also note that at the top of this swagger.yaml file, we specified
[a `basePath` of `/api/v1`](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/api/swagger/swagger.yaml#L8).
 This means the URL for this route is actually `/api/v1/user`, even though it's
 listed as `/user` here.  The basePath gets appended to the start of every path.

## Writing a Controller

Here's our very simple controller, found in
[src/swagger/controllers/user.js](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/controllers/user.js):

```js
// src/swagger/controllers/user.js

// This is a controller.

export function getUser(req, res) {
    // variables defined in the Swagger document can be referenced using
    // req.swagger.params.{parameter_name}
    const id = req.swagger.params.id.value;

    // This sends back a JSON response.  In a real application we'd
    // go to mongodb or some other application logic here.
    res.json({
        id,
        username: 'jwalton'
    });
}
```

This just returns back a fake "user" object.  Note that the return value of
the controller is ignored.  If you throw an exception, it will be propagated
back to the client (although maybe not in a pretty JSON format like you'd
expect), but if you try to return a Promise and that Promise rejects,
you'll just have an unhandled Promise rejection and your client will never
get a response.

## Configuring swagger-node-runner

Ok, now we have a definition of our API, and we have a controller which
implements this API.  We need an express middleware which glues
these together, and takes care of routing, validating incoming
requests to make sure they match the schema defined in the definition, and
calling into our controller.  This is where swagger-node-runner comes in.

swagger-node-runner uses the [config](https://www.npmjs.com/package/config)
module to load it's configuration from `/config/default.yaml` in the root of
your project.  If you're already using `config`, you can just add a `swagger`
entry to your config file.  If you're not using config, you can just pass all
the configuration directly to `swaggerNodeRunner.create`:

```js
// Stop swaggerNodeRunner from complaining about the lack of a config file.
process.env.SUPPRESS_NO_CONFIG_WARNING = 'true';

swaggerNodeRunner.create({
    appRoot: path.resolve(__dirname, '..'),
    swagger: path.resolve(__dirname, '../api/swagger/swagger.yaml'),
    fittingsDirs: ['lib/api/fittings'],
    ...
}, done);
```

(Edit: I've just discovered that swagger-node-runner calls `config` in
"strict mode", which means that if you run your app with `NODE_ENV=production`,
`config` will produce a warning because 'production.yaml' doesn't exist.  A
better solution might be to make a 'swagger' folder in your project, and tell
swaggerNodeRunner that this swagger folder is your "appRoot".  Then you can
either create 'swagger/config/default.yaml' and friends and put your
configuration there, or you can create empty files to appease `config`.)

At a minimum, the call to `swaggerNodeRunner.create()` needs to contain
`appRoot`, the path to the root of your source tree.  swagger-node-runner
uses this to resolve /config/default.yaml, and also other paths in the
configuration (but, weirdly, not the `swagger` definition file, so make
sure you `path.resolve()` it as shown above).  Also note that if you want to
specify the path to your swagger.yaml file, you must pass it directly to
`swaggerNodeRunner.create()` - it will not be loaded from default.yaml.

You can find documenation for all the options in the configuration
[here](https://github.com/swagger-api/swagger-node/blob/master/docs/configuration.md).
Note that in the latest version of swagger-node-runner, you need to add
'swagger_params_parser' to the bagpipes/swagger_controllers right after 'cors'.
If you generate a project with 'swagger' it won't be there, and it's not
mentioned in any of the documentation.  If you have problems with
`req.swagger.params` not being defined in your controllers, it's probably
because you're missing this.

You can see the config for our project
[here](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js).

By default, swagger-node-runner looks for a swagger definition file in
'/api/swagger/swagger.yaml', relative to your project root.  You can move this
to a different location, or even pass in a JSON object by passing in the\
`swagger` option to `swaggerNodeRunner.create()`.  (Although, as mentioned
above, swagger-node-runner will resolve `swagger` to the current working
directory, and not to the application root.)  Leaving it in
'/api/swagger/swagger.yaml' has the advantage that you can run
`npx swagger project edit`, and it will launch a nifty editor in a window where
you can edit your OpenAPI document (although it will use an older version of
the swagger editor.)

Note that 'swagger-node-runner' has no support for promises, so if
you're a fan of async/await, and you're on Node.js 8, you can do:

```js
import {promisify} from 'util';

// swagger-node-runner doens't support promises, so use promisify here.
const createSwaggerNodeRunner = promisify(swaggerNodeRunner.create).bind(swaggerNodeRunner);
```

If you're on an older version of Node.js, `util.promisify()` doesn't exist, but
you can use the [promise-breaker](https://github.com/jwalton/node-promise-breaker)
library to do basically the same:

```js
import pb from 'promise-breaker';

export async function makeServer() {
    ...

    const swaggerRunner = await pb.call(done =>
        swaggerNodeRunner.create(swaggerConfig, done)
    );

    ...
}
```

Creating the runner and integrating it with express looks like:

```js
    const swaggerConfig = {
        appRoot: path.resolve(__dirname, '..')
    };

    // Create a swagger middleware
    const swaggerRunner = await pb.call(done =>
        swaggerNodeRunner.create(swaggerConfig, done)
    );
    const swaggerExpress = swaggerRunner.expressMiddleware();

    // Note this line is equivalent to `app.use(swaggerExpress.middleware);`
    swaggerExpress.register(app);
```

(A minor bug as of this writing: in swagger-node-runner@0.7.3,
after writing the message body, swagger-node-runner will call `next()` to
pass control to the next express route, which means if you have any other
routes that match the URL, they will be run.  See
[#87](https://github.com/theganyo/swagger-node-runner/issues/87) for details
and a workaround, and
[PR #125](https://github.com/theganyo/swagger-node-runner/pull/125).)

The `swaggerRunner` instance has some useful properties;

* `swaggerRunner.api` is the Sway instance which powers the swaggerRunner.
* `swaggerRunner.bagpipes` is the bagpipes instance.

Wait... bagpipes?

## How Does This All Work?

Ok, if you've followed along to this point, you have now seen all the code
required to make this thing fly.  You can give it a try by running `npm start`,
and pointing a browser at
[http://localhost:10010/api/v1/user?id=54f0be26ae8aba260b8f6db7](http://localhost:10010/api/v1/user?id=54f0be26ae8aba260b8f6db7),
and you should get back a JSON reply like:

```json
{"id":"54f0be26ae8aba260b8f6db7","username":"jwalton"}
```

We already saw that the swagger.yaml file defines our API, and defines the
controller to call to run the API.  So swagger-node-runner is providing a
middleware that, for any route defined in the swagger.yaml file, will call into
the appropriate controller and run the appropriate function.

If you have a look at the
[configuration](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js)
for swagger-node-runner, you'll see where we define the directory to find
the controllers, and where to find mocks.  But... what's all this about bagpipes
and fittings?  What does Scottish music have to do with any of this?

[bagpipes](https://github.com/apigee-127/bagpipes) is a library that is, in
many ways, similar to express; a "fitting" is like an express middleware
function.  A "pipe" is a list of fittings that get called, in order.

So you'll notice that in the swagger-node-runner config, there's a
["swaggerControllerPipe" set to "swagger_controllers"](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js#L17),
and then if you look down in the "bagpipes" section you'll find a
["swagger_controllers"](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js#L29-L37),
which contains a list of "fittings" to run.  All of these fittings are
["built in" fittings](https://github.com/theganyo/swagger-node-runner/tree/07a706f461833ca1642981a61c8ce72e6a8a260b/fittings),
that come with swagger-node-runner.  You can
[write your own fittings](https://github.com/apigee-127/bagpipes#user-defined-fittings)
and add them into this chain as well, for example, to do customized
authentication or authorization.  In the next part of this series, we'll show
a simplified example fitting which does custom validation.

You'll also notice there's a route called "/swagger" defined in swagger.yml.
Going to /api/v1/swagger will return the JSON for the API specification.

```yaml
  # This makes it so you can get the swagger file from /api/v1/swagger.
  /swagger:
    x-swagger-pipe: swagger_raw
```

"x-swagger-pipe" here tells swagger-node-runner to use the custom
["swagger_raw" pipe](https://github.com/jwalton/node-swagger-template/blob/d2d9f6e1d326f1e227acae818b9ccdd231592f3a/src/swagger/config.js#L38-L40)
defined in the swagger-node-runner config.

## Next steps

In the next parts of this article, we'll talk about:
* Adding custom validation
* Steps to make this production ready
