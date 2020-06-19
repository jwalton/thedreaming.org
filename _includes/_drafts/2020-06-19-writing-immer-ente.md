# Writing immer-enten

I recently wrote immer-enten, a library for managing state in React.  That's not
too exciting, there are lots of libraries for managing state.  But, it has some
tricky bits, and I thought writing an article about it might help some people
understand the inner workings, and maybe understand React a little better.

## What's wrong with Redux?

Redux is a pretty popular framework for maintaining app-wide state in a React
app.  The problem with Redux is that it tends to be quite verbose, and have a
lot of boiler plate.  If we want to increment a counter, we need to store that
counter in our store, and then we need an action creator function which
generates an action, and then we need to pass that action to a reducer which
actually increments the counter.  That's a lot of code for `x++`.  Redux has
it's place, but I think we can come up with something a little more light weight
for smaller apps, and even for smaller subsections of larger apps.

But there are some nice things about Redux, and it would be nice if we could keep
them.  The Redux state is immutable, which is ideal in React.  React components
generally only re-render when their props change, so making it so props change
if and only if some descendant in the state tree changes is a good thing.

Another nice thing about Redux (and something a lot of other immer-based libraries
"get wrong") is that reducers are very easy to test.  They are just a function
that takes in some state and an action, and produces some new state.  You can
test them without involving React at all.  It would be nice if we could do
something similar.

## What's immer?

Immer is a very popular library which takes care of a lot of the "immutable" part
for us.  Basically, immer provides us with a `produce` funciton which takes in
our state, and some funciton to mutate that state, and with some clever use of
proxies it generates a new state object that only has the changes we made.
Here's a really simple exmample:

```ts
const user = {
    name: 'Jason',
    credits: 100,
    features: {
        hair: 'red',
        eyes: 'blue',
    },
};

const updated = produce(user, draft => {
    draft.credits++;
});

console.log(user.credits); // Still 100
console.log(updated.credits); // 101
// Note that parts of the state tree we didn't update are still exactly the same object
console.log(user.features === updated.features);
```

The applications in React should be pretty obvious here - we can write this "draft"
function that gets passed into `produce`, and update our state like any normal
javascript object, without any fancy "actions" or "reducers".

## What we're trying to build

What we want to do is to define some "initial state", possibly given to us from
the server if we're doing server-side-rendering, and then a set of "actions" which
operate on that state.  Our actions are going to be pretty boring functions that
just operate on the data directly, so they don't need to be too fancy.

Actions may be async, and we want updates to the state to be "atomic", so we'll
want our actions to have access to some kind of "updateState()" function.  For
example, if you have an action that's saving something on the server, you
might want to set an `updating` flag in your state, then save to the server,
then set `updating` back to false.  Something like:

```ts
async function updateTheThing() {
    updateState(state => { state.updating = true; })
    try {
        await fetch('/update', { method: 'post', ... });
    } finally {
       updateState(state => { state.updating = false; });
    }
}
```

There's cases where `getState()` are handy too.

Once we have all our state and actions defined, we're going to want to be able
to get access to t

## Subscribing to state changes

* Can just store state right in the provider, but then every time the state
  changes, all components using hooks will re-render.