## Adding a Pretty UI to Explore the API.

[swagger-ui](https://github.com/swagger-api/swagger-ui) is a well documented,
responsive UI for swagger files.  It will show an API which lets users browse
your API documentation and try out live examples.  You can see a
[live demo here](http://petstore.swagger.io/).

![swagger-ui screenshot](/images/swagger-ui.png)

There's two versions of swagger-ui; as the documentation says: "`swagger-ui`
is meant for consumption by JavaScript web projects that include module
bundlers, such as Webpack, Browserify, and Rollup. ... In contrast,
`swagger-ui-dist` is meant for server-side projects that need assets to serve
to clients."

Setting this up in our express project is a breeze.  First we need to generate
an HTML file that shows the swagger UI.  There's an example in our project
[in /static/api/v1/index.html](https://github.com/jwalton/node-swagger-template/blob/master/static/api/v1/index.html#L76).
Note that we need to set the path to our swagger JSON file.

Then we just need to serve the files:

```js
import {absolutePath as pathToSwaggerUi} from 'swagger-ui-dist';

...

app.use('/api/v1', express.static(pathToSwaggerUi()));
app.use(express.static(path.resolve(__dirname, '../static')));
```

And now you can start the project, visit
[http://localhost:10010/api/v1/](http://localhost:10010/api/v1/), and get
beautiful docs.

## Host and Schemes

If you have a look at the swagger.yaml file, you'll note that it has a `host`
and a `schemes` section.  These values get used by `swagger-ui` to generate
requests.  Clearly, in production, we don't want these to be `localhost:10010`,
and we likely want to get rid of `http` from `schemes`.  We fix this by
pre-loading our swagger definition before passing it to swagger-node-runner.

```js
async function loadSwaggerDefinition() {
    const swagger = await sway.create({definition: SWAGGER_FILE});
    const definition = swagger.definitionRemotesResolved;

    if(process.env.NODE_ENV === 'production') {
        definition.host = 'thedreaming.org';
        definition.schemes = ['https'];
    }

    return definition;
}
```

We can pass this result to swaggerNodeRunner with:

```js
    swaggerNodeRunner.create({
        appRoot: path.resolve(__dirname, '..'),
        swagger: await loadSwaggerDefinition(),
        ...
    });
```

Note that we use `sway` here, rather than something like `yaml-js` to read the
swagger.yaml file.  This is because an OpenAPI document can be
[split across multiple files](http://azimi.me/2015/07/16/split-swagger-into-smaller-files.html),
and `sway` does the hard work of finding those files and merging them for us.

If you run the sample app with:

```sh
$ NODE_ENV=production npm start
```

You'll notice that if you visit [http://localhost:10010/api/v1/](http://localhost:10010/api/v1/),
you'll see that the URL for your app listed in the UI is now
"https://myproductionserver.com", and if you try and of the examples, they'll
try to visit that server.

Also note that you can simply omit the "host" line altogether from the swagger
file.

## Authentication and Authorization


## swagger-jsdoc

One thing you'll probably notice right away - if you're writing a large API,
you're swagger.yaml file is quickly going to grow out of control.

`swagger-jsdoc` provides a way to generate your swagger.yaml file from
js-doc comments.

## Handling exceptions

If you try to `throw new Error("boom")` from inside a controller, you'll notice
that the client will get back a decidedly non-JSON text error, complete with
full stack trace.  On a production system, we at a minimum want to hide the
stack trace.


