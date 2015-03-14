---
title: "Ajax Calls with React and Flux"
tags:
- react
- flux
- development
- javascript
---

There's a lot of confusion about how to use AJAX to fetch data for a React app.  This is a problem
with many different solutions, and in this article we're going to examine some of the relative pros
and cons of each.

<!--more-->

## The Problem

To borrow a picture from the [Flux](http://facebook.github.io/flux/docs/overview.html) website:

![Flux action dispatch diagram](/images/flux-diagram.png)

To recap; "action creators" are functions which generate actions.  Actions are fed to the dispatcher
which distributes the action to any interested "stores" which contain data and business logic.
If stores are changed, then the view is re-rendered.  Data from the stores is either fed
to views as "props", or else "controller-views" will fetch required data from stores and pass this
data down to child views as props.

Actions are, by their nature, synchronous.  Most Flux implementations will prevent you from
dispatching a new event from inside an event handler, to prevent cascading actions and action
cycles, which are difficult to reason about.

Any non-trivial web app, however, will eventually have to retrieve data from the network.  How
do we handle this data in our Flux app?

## Data as State - An Antipattern

[react-async](https://github.com/andreypopp/react-async) has the component itself fetch any async
data needed to render the component and store this in the component's `state`.  The project's
README declares that this is an anti-pattern.

There are lots of reasons why this approach isn't a good one.  First, `state` is intended to store
state about the UI itself, and not store data.  React is a very functional apporach to building
a UI; a React component is essentially a function which describes what your UI looks like at
any point in time.  Given the same inputs, your React component should produce exactly the same UI.
Adding an AJAX call into the middle of rendering the component throws this out the window - passing
data in will cause your component to render, and then render itself again at some point in the
future when the AJAX call is fulfilled.

Aside from the semantics; if you're using Node.js and want to render your components server-side to
build an isomorphic app, you are immediately going to run into problems with this approach, as your
components will have already rendered themselves to a string by the time they get data.

## Data as an Action

A very common solution to this problem is to treat incoming data as an action.  Suppose,
for example, that we are writing an application which displays a blog.  The user navigates to a
new article.  We have an action creator:


    function showArticle(articleId) {
        dispatch({type: "SHOW_ARTICLE", id: articleId, state: "loading"});
        $.ajax({
            url: "/article/#{articleId}"
            success: function (data, textStatus, jqXHR) {
                dispatch({type: "ARTICLE_LOADED", id: articleId, state: "ready", content: data});
            }
        });
    }

Here the store will receive a "SHOW_ARTICLE" actions with the state "loading" (which would
cause your component to perhaps show a nice "loading" message) followed some time later by an
ARTICLE_LOADED actions (which would re-render your component with actual content.)

If you're building an application using a technology like websockets, where the server can push
data to your client, then actions are a very natural way to deal with data.  If you are building
a web-based chat application, for example, then it's easy to see how when you receive a new chat
message over socket.io, you would generate a "MESSAGE_ADDED" action.

In the AJAX case, one question is where the AJAX call should live.  In the example above, we show
it happening in the action creator.  This seems like a natural place for it, since creating and
dispatching actions is what the action creators are all about.  On the other hand, this means
the action creator needs to know what data to fetch, which puts a little chunk business
logic into your action creator.  In this very simple example, we're fetching the article from the
server every time it is shown, but what happens if we want to check and see if the article is
already cached in the store before making the AJAX call?  Do we call into the store from the action
creator?  It's easy to see how we can quickly end up in a scenario where the action creator and the
store are tightly coupled - when one changes, the other needs to change with it - which is defintely
something we'd like to avoid.  Never the less, this is exactly the approach used by Yahoo's
[flux examples](https://github.com/yahoo/flux-examples/blob/master/chat/actions/createMessage.js).

Another approach is to put the ajax call in the store itself.  The store receives a "SHOW_ARTICLE"
action, checks to see if the article in question is already in the store; if it is, we
render the view immediately.  If it isn't then the store itself creats an AJAX request and then
generates an "ARTICLE_LOADED" action.  This keeps all our business logic together in one place,
but it also means handling an action can generate another action (albeit asynchronously.)

Putting the AJAX call in the store can also have interesting consequences when you're building an
isomorphic application; the author of Fluxxor has an
[example project](https://github.com/BinaryMuse/isomorphic-fluxxor-experiment) which works this way.
To render on the server, we render the component, which tries to fetch data from the store, which
causes an async loading action (this would be an AJAX call on the client, but an async function
call server side), which causes the store to update, which causes us to re-render the component.
This works, but has the obvious downside that components need to be rendered twice on the server.
You could get around this by ensuring the appropriate data was pre-populated into your stores
before calling the first render, but this means you need to know in advance what data is going to
be requested by each component.

There are various ways you can combine these apporaches; you could make the action creator function
a member of the store itself.  This provides a lot of advantages; your business logic all lives in
the store, but at the same time you have a clear demarcation between functions that generate
actions and functions that handle actions.  This works well provided that an action doesn't need to
interact with multiple stores.  You could also make dispatching actions strictly the purview of
the action creator, but have the action creator make an async call into the store to fetch any
required data.

I'm not sure that any of these approaches are "best"; I think which approach you use depends on
the problem you are trying to solve.

Do you have a different way of approaching this?  Any obvious pros or cons you think I've missed?
Sound off in the comments below!
