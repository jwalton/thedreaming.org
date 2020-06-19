---
title: "Isomorphic React Tutorial"
tags:
- react
- development
- javascript
---

This is an article that explains how to build an "isomorphic" Node.js web-app using React and Flux.

There are a lot of good articles out there that explain, at a high level, what's involved in
building such an application, and there are quite a few projects on github that purport to be
good "starter templates" for building such an app.  This article is going to try to be somwhere
in the middle - a detailed look at how such an application is built from the ground up, explaining
some of the design decisions and trade offs we're going to make along the way.

<!--more-->

This assumes you have played around a bit with React and Flux, or at least are familiar with
thec concepts involved.  If you aren't, then check out the [React](http://facebook.github.io/react/docs/getting-started.html)
and [Flux](http://facebook.github.io/flux/docs/overview.html#content) tutorials from Facebook.

## Is This a Good Idea?

There are a few arguments for why you'd want to build an isomorphic app, but some of them might not
be true:

Search Engine Optimization (SEO) - The argument goes that search engines like google don't run
JavaScript when they crawl your site, so if your site is entirely rendered client-side, then
on Google your site will show up as a "Loading..." screen.  This hasn't been true since around
[May of 2014](http://googlewebmastercentral.blogspot.ca/2014/05/understanding-web-pages-better.html),
though - Google now runs the JavaScript on your site when they index it.

Performance - The argument goes that forcing the client to render content, espeically right when
the client is busy downloading resources from the server and parsing JavaScript and style sheets,
is going to delay the time it takes until your user sees a functional page.  There is at least
some empirical evidence that [this is not actually true](http://www.onebigfluke.com/2015/01/experimentally-verified-why-client-side.html) however.  On the other hand, if you have a very large JavaScript application,
you can render a page and display it on the client before the client has even downloaded your
application.  Google recommends that your [app be under 14K](https://developers.google.com/speed/docs/insights/mobile) if you want it to display in under one
second on a mobile device; it's hard to imagine building a full blown modern one page app in under
14K, but certainly for most apps you could render a (mostly) functional first page for the client to
look at while you're downloading the rest of the app.  Some parts of your application may not
work until the full javascript has been downloaded and React has had a chance to hook up all the
event handlers, of course.

Clients without JavaScript - Some clients won't have JavaScript enabled at all.  For many web apps,
such as the simple blog example we're going to detail below, you can actually build an application
that is fully functional for clients that don't have JavaScript enabled with a little forethought.
The basic idea is that where ever we have a UI element that changes the page, we make it a link.
If a user with JavaScript enabled clicks on the clink, we prevent the default action and do whatever
we need to do to refesh the page in code.  If the user has JavaScript disabled, then clicking on
the link will cause a page load, and the server can render the new page content for the user.

On the one hand, it's simpler to build an app that isn't isomorphic.  On the other hand, once you
set up the framework to build an isomorphic app, most of the headache is behind you, and going
isomorphic may influence some key design decisions up front.  So, be sure this is something you
need before you spend time adding this complexity, but if you think you're going to need it then
invest up front and get it out of the way.

## The Basics

The basic idea is to build a single page web-app which we can render on either the server or on the
client.  As an example, we're going to build a simple blog application.  There will be an index
page which shows a list of articles available, and clicking on an article title will show you
the contents of that article.  Every article will have a unique URL of the form
`myblogapp.com/article/{id}`.

This is a pretty simple example, but it actually has a lot of interesting challenges to solve from
a design perspective.

## Entry Points

There are two fundamentally different ways that a client can view a blog post.  First, if the
client starts at our index page and clicks on a blog post, then our app will need to pull the
necessary data from the server and then render the new page client side.  The client could,
however, go directly to the URL for the blogpost (from a search engine or a bookmark, for example)
in which case the app will again need to pull the necessary data (although direct from a database
this time instead of from an AJAX call, obviously) and render the new page server side.

Here's a detailed step-by-step break down of what needs to happen in these two cases (ignoring
"how" they get done, from an implementation standpoint):

### Client Side Entry Point:

* User clicks link
* Client updates URL
* Render loading page
* Load up blog article data from server via AJAX call and put in ArticleStore
* Render view of blog on client

### Server Side Entry Point:

* User navigates to page
* Server parses URL from client
* Load up blog article via DB call and put in ArticleStore
* Render view of blog to string
* Serialize ArticleStore, send it and the rendered view to client
* Client decides what view to show
* Client re-renders view from store (to get React to hook up all the event handlers)

In the server rendered case, we actually end up rendering the same view twice.  On the server, we
render it to an HTML string to send to the client.  This is going to be just HTML though, without
any event handlers.  We need to re-render the view on the client over top of the server rendered
view.  React's virtual-DOM ensures this will be a fairly fast operation.

Even though these two cases have a lot of differences, there's core shared behavior here; in both
cases, we need to decide what information needs to be requested (from the database or via AJAX),
this data needs to be loaded into the ArticleStore, and finally the view needs to be rendered.  We
don't want to duplicate code between the server and client, which means this core behavior should
be in shared code.

Sharing the view code is relatively easy - in both cases we have React code which will load data
from the stores and render it.  Deciding what data needs to be retrieved and which components need
to be rendered is more interesting.

The biggest problem we're going to run into here is that the way the client and server intiate these
actions is quite different; on the client, when the user clicks on an article in the index, we'd
typically use a click-handler which would call into the action creator to perhaps generate a
"loading article" action (causing the view to re-render itself with a "loading" screen), then kick
off an AJAX request which would later result in a "show article" action, causing ArticleStore to
update.  In most frameworks, the view will update itself when the stores change.

On the server side, though, things look quite different.  The impetus for all of this is parsing
a URL (a URL which ideally should be the same as the URL we would generate on the client when
clicking on the link.)

After parsing that URL, we need to populate the stores; the way we do this
on the client is via an action creator, but really there's no need to dispatch actions on the
server - we just need to fetch the data and load it into the stores.  In the interest of maximizing
code sharing, we could create a dispatcher and stores on the server, and then call into the same
action creator as on the client to fetch data, but we can't just re-render the view over and over
again as as the stores change - we only want to render the view once, and then return it to the
client.  This implies that the server needs to know when when all the actions are "done", which
means our action creators need to either take a callback or return a Promise.  Note this is almost
exactly the approach taken by Yahoo's
[fluxible](https://github.com/yahoo/fluxible/blob/master/docs/api/Actions.md).

There's a bunch of different concepts that are tied up together here; clicking on a link fires an
action to, and sets the URL.  Navigating to that URL needs to fire the same action on the server.
In both cases we want to fetch data and populate stores.  There are a lot of different libraries
out there that can tie these all together for you, the most common of which at the moment is
[React-Router](https://github.com/rackt/react-router).
[Fluxible](https://github.com/yahoo/flux-router-component) has a router component which fulfills
much the same roll.

## A Simple React App

First, let's set up a quick express project.  If you want to skip this bit, you can clone
[this project](https://github.com/jwalton/node-isomorphic-flux-react) and checkout the
"01-setup" tag.

Create a new directory for your project.  In this new folder, start with a bare bones package.json
file:

    {
      "name": "isomorphic-react-flux",
      "version": "0.1.0",
      "description": "A framework for building isomorphic applications with React and Flux",
      "scripts": {
        "start": "node src/server/app.js"
      },
      "private": true,
      "license": "MIT"
    }

Then use NPM to install some dependencies:

    npm install --save express compression body-parser morgan jade browserify-middleware react reactify

Make some folders:

    mkdir src
    mkdir src/server
    mkdir src/client
    mkdir views

Create `src/server/app.js`, which will be our Express web server:

    var path        = require('path');

    var bodyParser  = require('body-parser')
    var browserify  = require('browserify-middleware');
    var compression = require('compression');
    var express     = require('express');
    var logger      = require('morgan');

    var app = express();

    app.set('port', process.env.PORT || 8080);

    app.set('views', path.join(__dirname, '../../views'));
    app.set('view engine', 'jade');

    app.use(logger('dev'));
    app.use(bodyParser.json());
    app.use(bodyParser.urlencoded());
    app.use(compression());

    // Server browserify bundle to client.
    app.get('/client.js', browserify('./src/client/index.js', {
        transform: [['reactify', {es6: true}]]
    }));

    // Routes
    app.get('/', function (req, res) {
        res.render('index');
    });

    // 404 for any other pages
    app.use(function(req,res,next) {
        var err = new Error('Not Found');
        err.status = 404;
        next(err);
    });

    // Start the server
    app.listen(app.get('port'));

    module.exports = app;

Create `views/index.jade` which is our default HTML view:

    doctype html
    html
        head
            title React Demo
            link(rel='stylesheet', href=cssUrl)
            meta(name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1")
        body
            #content
            script(type='text/javascript' src='/client.js')

And finally create `src/client/index.js`, which is going to be bundled into our client-side
application by `browserify-middleware`:

    var React = require('react');

    var MyComponent = React.createClass({
        displayName: 'MyComponent',
        render: function () {
            return <div>Hello World</div>
        }
    });

    React.render(
        React.createElement(MyComponent, null),
        document.getElementById('content')
    );

If you run `npm start` and point a web browser at http://localhost:8080, you should see
"Hello world".  We've just created a super simple Express app that can serve up JavaScript
apps built with React and JSX.  I don't want to go into too much detail describing what's going on
here, because there's other tutorials that do that, but hopefully this is simple enough to follow.

### How does the server kick off the correct action to load the store?

### How do we end up using AJAX on the client and direct DB calls on the server?