---
title: "Why are Weakmaps in Javascript not Enumerable?"
tags:
- javascript
- es6
- java
---

Recently a colleague of mine noticed this in the [MDN description of WeakMap](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/WeakMap#Why_WeakMap):

> Because of references being weak, WeakMap keys are not enumerable (i.e. there
> is no method giving you a list of the keys). If they were, the list would
> depend on the state of garbage collection, introducing non-determinism. If you
> want to have a list of keys, you should use a Map.

My co-worker wondered what this meant exactly?  Where does the non-determinism
come from?  Doesn't the state of WeakMap still depend on garbage collection
even if you can't enumerate the keys?

<!--more-->

To understand this, perhaps it's best to examine a hypothetical JavaScript where
the keys of `WeakMap` are enumerable.  This would let you do some interesting
things:

```js

function waitForGc(obj, callback) {
    const map = new WeakMap();
    map.set(obj, 1);
    obj = undefined;

    function test() {
        const keys = Array.from(map.keys());
        if(keys.length > 0) {
            setTimeout(test, 1000);
        } else {
            callback();
        }
    }
}
```

You could call this function, pass it an object and a callback, and
(approximately) when that object was garbage collected, this would call your
callback to let you know.

The key insight here is that our hypothetical `map.keys()` returns something
different depending on the state of garbage-collection.  If `obj` has been
garbage collected, it returns an empty set, whereas if it has not been,
`map.keys()` will return an iterator with one object in it.

Now, you might be thinking "Can't I do this anyways?  Can't I just call
`weakMap.get(obj)` to check to see if `obj` has been garbage collected?"  The
answer is no; if you had a reference to `obj` to pass into `weakMap.get()`, then
clearly `obj` has not been garbage collected, because you have a (strong)
reference to it.  There's a `WeakMap` in JavaScript, but no `WeakReference` like
in Java.  So the behavior of `weakMap.get()` is deterministic, and doesn't rely
on the state of what has or hasn't been garbage collected (at least, from your
viewpoint as the programmer).

Note that being able to detect changes in garbage-collection state might allow
some interesting side-channel attacks, which was brought up as one of the
[reasons not to allow it](http://tc39wiki.calculist.org/es6/weak-map/) in the
original proposal:

> A key property of Weak Maps is the inability to enumerate their keys. This is necessary to prevent attackers observing the internal behavior of other systems in the environment which share weakly-mapped objects. Should the number or names of items in the collection be discoverable from the API, even if the values aren't, WeakMap instances might create a side channel where one was previously not available.

## Java WeakReference, SoftReference, and PhantomReference

There's a sort of similar and related problem in Java regarding garbage collection
of objects referenced by `WeakReference`s.

In Java, in addition to `WeakMap` we have a `WeakReference` - this is like a
pointer to an object that "doesn't count" when the garbage collector is trying
to figure out which objects are eligible for garbage collection:

```java
    User user = new User('Jason');
    WeakReference weak = new WeakReference<User>(user);

    user = null;
    weak.get(); // returns the user, or null if the user has been GCd.
```

Java also has a `SoftReference`, which is just like a `WeakReference`, except
the VM will try to keep the object in memory as long as it can, which makes it
useful for building caches (especially, if you're not careful, caches that fill
all of memory with useless unused objects).  Also, `SoftReference` has been around
since Java 1.2, but even though it was documented as trying to keep objects
in memory longer, in Java 1.4 and lower it was implemnted exactly the same as
`WeakReference`.  YMMV depending on the VM you are using.

Finally, Java has a `PhantomReference`, which is just like a `WeakReference` or
a `SoftReference`, except you're not allowed to `.get()` the object that it
references.  That's right - it's like a pointer you're not allowed to
dereference.  That sounds totally insane and useless, until you learn about
`ReferenceQueue`s.

### ReferenceQueues

When you create a `WeakReference`, you can optionally add it to a `ReferenceQueue`
by passing such a queue in the constructor. You can then `queue.remove()` which
will block until a reference is ready to be garbage collected, and return that
reference to you. (Or, `queue.poll()`, which returns a reference if one is ready
or null if none are, if you don't want to dedicate a whole thread to watching
references.)

This is exactly the mechanism you'd use to implement a `WeakMap` in Java; every
time someone adds an object to your map, you'd create a `WeakReference`, and
then use the `WeakReference` as a key in a regular `Map`. But, you need to clean
up that key in your `Map` when the object is ready to be GCed (since otherwise
you'd have a `Map` with a ton of `WeakReference` keys for GCed objects, and
associated values you would never access again, and you'd just slowly eat up
all of memory).  To do this, you'd add the WeakReference to a ReferenceQueue,
and then when the object is about to be GCed, Java would effectively notify you
about it and you could remove the WeakReference from your Map.

But, the `ReferenceQueue` presents a unique problem in Java; When the object is
ready to be GCed, the ReferenceQueue is going to pass you back that WeakReference.
At that point, you can say "Haha Java! Not today!" and call
`array.push(weakReference.get())` to create a new strong reference to the object,
which makes it no longer eligible for GC.

This sucks for Java. If you create a `WeakReference` to an object, Java needs to
figure out the object is ready for GC, then before it GCs it, it needs to call
any reference queues, and then it needs to figure out if the object is ready for
GC **again**. This "two-stage" GC is expensive. But `PhantomReference` gets
around this; because you can't `.get()` the object, Java doesn't need to do the
two-stage GC, so it's cheaper (although of more limited use).

So, at the end of the day, I suppose the JavaScript folks looked at all that mess
in Java and said, "Nope, we're not doing any of that."