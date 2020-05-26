---
title: "Avoiding CSRF Attacks with API Design"
tags:
  - security
  - XSS
  - API
---

Cross-site request forgery (CSRF) attacks are a type of attack where a website you
don't control tries to send commands to your website, using your customer's
cookies. Today we're going to look at a few ways you can avoid CSRF attacks,
mostly just by being careful about how you design your API.

<!--more-->

The basic idea behind a CSRF attack is that one of your users uses their browser
to log into your website (let's say "awesomebank.com" as an example), and then
they visit a malicious website with the same browser, and that malicious website
sends a request to your website. In certain cases, the browser will send
cookies for your website along with that request, even though it came from the
malicious website. From your server's perspective, you get an API call from
an authenticated user, so you'll probably end up doing what the malicious site
wants you to do.

Fortunately, modern browsers have all sorts of protections in place to prevent
this sort of thing. Unfortunately, if you don't know how these work it can be
easy to accidentally bypass those proections. This article is going to give you
some practical advice you can use to help avoid that.

## Never use GET to modify state

You're building this website for awesomebank.com, and you need an API that will
let you send money to a customer by email. No problem, let's make an endpoint
that you can GET and pass some query parameters to in order to send some money.
Client side, in a react form, we might do something like:

```js
const onClick = () => {
  fetch(
    "https://awesomebank.com/api/sendMoney?amount=100&to=friend@gmail.com"
  ).catch((err) => showErrorMessage(err));
};
```

You probably already know this is a bad idea; GET requests should never change
state. For one thing, the browser might decide to cache this GET request, so
doing this twice on the client might end up only doing it once on the server.
Some HTTP clients also assume that GET requests are safe to send again, so a
browser or proxy might send this request multiple times if it fails or times
out.

But from a security perspective, this is an exceptionally bad idea. A malicious
website on evilcorp.com could do something like:

```html
<img
  src="https://awesomebank.com/api/sendMoney?amount=100&to=mrevil@evilcorp.com"
/>
```

Every time a customer who is logged in to your site visits evilcorp.com, they'll
see a broken image. Every time they see that broken image, they'll send \$100 to
Mr. Evil. This is obviously not a desirable state of affairs.

Now, you might have heard of something called the "same origin policy" and wonder
why it doesn't protect you here? The basic idea behind the same origin policy
is that a website from a given "origin" (the domain and port number in the URL)
can't access data from another website. This is true, but there are exceptions
to it - a web site is obviously allowed to link to another website, or else
the Internet wouldn't be very useful. Websites are allowed to load scripts
and images from other websites - this is how a CDN works. Basically, (to
over-simply slightly) the same origin policy is only going to protect you if the
request in question was made from a script.

In this case, the browser has no idea that this `img` tag is anything other
than a normal GET request - it's going to send the request to awesomebank.com,
and it's going to send along any cookies for that website. It will probably
get back some sort of JSON response, hence the broken image, but evilcorp.com's
website is going to end up stealing your customer's money anyways.

Fortunately, it's easy to avoid this; just don't let GET requests modify state.

## Don't accept form encoded bodies

Let's pretend it's 1995, and you're building a website. You might write
an HTML form like this:

```html
<form method="post" action="https://awesomebank.com/sendMoney">
  <div>
    How much do you want to send:
    <input name="amount" />
  </div>
  <div>
    To:
    <input name="to" />
  </div>
  <input type="submit" value="Send my moneys!"></button>
</form>
```

When you click on that submit button, this is going to send a POST request
to `https://awesomebank.com/sendMoney`, with the `amount` and `to` in the body
and with a content-type of "application/x-www-form-urlencoded". If there were
some file attachments in this form, it would use "multipart/form-data" instead.

The problem here is that our attacker on evilcorp.com can write a page like this:

```html
<form method="post" action="https://awesomebank.com/sendMoney">
  <input name="amount" type="hidden" value="100" />
  <input name="to" type="hidden" value="mrevil@evilcorp.com" />
  <button type="submit">Click here for free money!</button>
</form>
```

This is a little better than the "img" example above, because here at least a
user has to click on a button to get their money stolen, and when they click on
that button they're going to get back what to them is probably a gibberish
page of JSON data. But, it still lets an attacker execute commands on your
server.

You might be surprised that the same origin policy doesn't protect you here, but
again the same origin policy only really applies to scripts, and that "form"
tag isn't one. Part of the problem here is that the same origin policy wasn't
arround in the early days of the web, so there were lots of websites that would
have been broken if these rules had applied to forms.

(And actually, the same origin policy wouldn't even protect you here in a script,
because a GET or a POST with a form encoding is is what's called a "[simple request](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Examples_of_access_control_scenarios)"
from a CORS perspective, and scripts are allowed to make simple requests,
they're just not allowed to read the result. The request will have "evilcorp.com"
in the "origin" header, and you can set up your server to detect that, but in
the default case, most servers will be vulnerable.)

Now, this is probably not how you're writing your forms. You're probably using
React or Angular or Vue, and your forms probably have a submit handler that
calls the WHAT-WG fetch API or something similar, and sends data as
"application/json" encoded data. That's all good, and you might think you have
nothing to worry about.

But, I've seen a plenty of express.js apps that do something like this:

```js
app.use(bodyParser.json());
app.use(bodyParser.urlencoded());
```

That second line looks so harmless, but it enables decoding
"application/x-www-form-urlencoded" on all inbound routes. And once you enable
that, once your API on the server side accepts bodies encoded with "application/x-www-form-urlencoded", then evilcorp.com can build their form.

If you are writing an app that uses progressive enhancement - in other words
an app that works when JavaScript is disabled, then you have to accept these
form-encoded inputs.  You don't have a choice, because that's all a browser can
generate.  In this case, there are other methods you can use to protect yourself
which we will discuss below.  If you're building a website that requires
JavaScript to operate, though, then one option is to simply not accept any
request with a content-type of "application/x-www-form-urlencoded",
"multipart/form-data", or "text/plain" in the first place, and you won't be
vulnerable to this.

One thing especially to watch for - if you have an endpoint that doesn't expect
a body (say an endpoint for marking a post as "seen", where the ID of the post
is in the URL, so you don't need anything in the body), make sure these
endpoints return a 400 if there's an unexpected body, otherwise they may be
vulnerable.

## Don't disable the same origin policy

Let's pretend it's 2020. We're going to build our banking website using the
JAM stack, because that's all the rage. We'll have a static gatsby.js site
which we'll host in an S3 bucket at www.awesomebank.com, and then we'll have
some lambda functions to actually implement our API, which we'll host behind
an API gateway at api.awesomebank.com.

Except, when we try this, whenever our client tries to PUT or POST or DELETE,
you get back a 403. And when we look in our server logs, all we see is a
bunch of OPTIONS requests. What's is going on?

It turns out, we've fallen victim to our friend the "same origin policy".
"www.awesomebank.com" and "api.awesomebank.com" are, in fact, two different
origins, so when a script from one tries to POST with content-type
"application/json" to the other, the browser does what's called a "Cross Origin
Resource Sharing (CORS) preflight" request - it sends an "OPTIONS" request to
api.awesomebank.com with an "origin: www.awesomebank.com" header to check and
see if api.awesomebank.com wants to allow this request.

That's right - all these cases where we wanted the same origin polciy to protect
us, it did nothing. Now, the first time we come across it actually working,
it's getting in our way.

So we hop on stack overflow, and [they tell us](https://stackoverflow.com/questions/14256732/cross-domain-ajax-results-in-403-forbidden)
to try this (example in express.js, and taken from a real product, but hopefully
this is easy enough to read even if this is not your lingua franca):

```js
app.use(function (req, res, next) {
    res.header('Access-Control-Allow-Origin', '*'); // NEVER EVER DO THIS!
    res.header('Access-Control-Allow-Credentials': 'true');
    res.header('Access-Control-Max-Age', 60 * 60 * 24 * 30);

    // Intercept OPTIONS method
    if (req.method === 'OPTIONS') {
        return res.sendStatus(200);
    } else {
        return next();
    }
}
```

And this works! But there's two problems here. First, we took security advice
from stack overflow, and sadly this rarely goes well. Second, we've just
disabled the same origin policy for our whole API. We've told the browser to
let any other site access the API, so now evilcorp.com doesn't even need to mess
around with IMG tags or forms, they can write a script tag like this:

```html
<script>
  fetch("https://awesomebank.com/api/sendMoney", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ amount: 100, to: "mrevil@evilcorp.com" }),
  });
</script>
```

Same origin policy _would have_ prevented this, but we disabled it, so now
evilcorp can steal all our clients' money, yet again. (Hope we have good
insurance.)

To protect against this; if you do need to allow cross-domain requests, instead
of allowing access to "\*", pick a whitelist of origins that are allowed to
access your API and only allow those in.  This means you need to check the "origin"
header that the client sends, and if it's one that should be allowed, add
the following headers to your reply:

```
Access-Control-Allow-Origin: www.awesomebank.com
Access-Control-Allow-Credentials: true
Vary: Origin
```

Note the `Vary: Origin` which tells the browser that headers might change
depending on what origin is making the request.

If you're writing an express.js app, check out the [cors](https://github.com/expressjs/cors#configuring-cors)
package, which will let you whitelist a specific origin, or even let you call a
function to check an origin dynamically. (But make sure you pass in an `origin`
option, because sadly the default here is to allow any origin.)

## Write negative test cases

When you're writing test cases for your API, CSRF attacks are often overlooked.
But I've seen a junior developer check in a change with THE comment
"We keep seeing these OPTIONS requests failing in the logs. Not sure what these
are, but let's clean up the errors by just always returning 200 for OPTIONS."

If you're familiar with how CORS works, that's a pretty face-palm worth sort of
change.

Write some test cases that try sending an OPTIONS request to your API with an
`origin: evilcorp.com" header, and make sure you get back an error, or at least
don't get back an "Access-Control-Allow-Origin" header. Try sending data encoded
as "application/x-www-form-urlencoded" to an endpoint that is expecting
"application/json" (or to an endpoint that doesn't expect a body) and make sure
this fails.

Once you've read this article, you know the "rules" for safely handling
these requests, but don't assume everyone who works on your code base will (or
even that you'll remember them a year after reading this); make the rules
explicit with tests.

## CSRF Tokens

Let's say you want to write a web page that will work, even if JavaScript is
completely disabled. In this case, you need to write an API that accepts data
using "application/x-www-form-urlencoded" encoding. There's no helping it,
because this is all a browser can generate without JavaScript.  How do you
secure this endpoint against CSRF attacks?

One way to secure yourself here is to use something called a CSRF token.
The basic idea is to generate a random token and store it in your user session,
then make it so the CSRF token is either submitted by forms in a hidden field
or added as an extra "x-csrf-token" header in each API call. Server side, you
can check to make sure the CSRF token matches the one stored in the session.
Since it should be impossible for an attacker to get the CSRF token (the same
origin policy _does_ protect javascript from reading the contents of a response)
it makes it much more difficult for an attacker.

Many platforms have CSRF token support built in, so check your platform and
see what's available. For express, [csurf](https://github.com/expressjs/csurf)
is an excellent library for CSRF token suport.

Note that you only really need CSRF tokens for what [CORS calls "simple requests"](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS#Examples_of_access_control_scenarios);
for example a GET, or a POST with a content-type of "application/x-www-form-urlencoded",
"multipart/form-data", or "text/plain". If you're POSTing "application/json"
data, then you're already safe because of the same origin policy.

"[Double submit cookies](https://medium.com/cross-site-request-forgery-csrf/double-submit-cookie-pattern-65bb71d80d9f)" is a technique very similar to CSRF
if you're looking for something stateless.

Special care is needed here if your website is on a subdomain, and other websites
are available on other subdomains under the same domain.  For example if your
website is "bank.myfreehosts.com" and someone else can create a website at
"test.myfreehosts.com", either one of your sites can create cookies for
"myfreehosts.com", so you need to be careful that the cookie you're reading is
really the one you set.  In these cases, make sure your cookie is encrypted
with a secret only your server knows.

## Check the origin header

This is perhaps the simplest method of preventing CSRF attacks; if you know what
the origin header is supposed to be, check the origin header on your server.
All browsers will insert an origin header for cross-domain requests. Just note
that browsers (and non-browser clients such as a mobile apps) will not insert an
origin header for "same origin" requests, so you should allow requests with no
origin header.

## Use SameSite cookies

One thing you might be wondering - when evilcorp.com sends a request to
awesomebank.com, why are the awesomebank.com cookies being sent at all? Doesn't
this seem very insecure by design? Well, there's a relatively new standard
called "SameSite" cookies which will stop those cookies from being sent. When
you set your session cookie, set it with:

```
Set-Cookie: session=blahblahblah; SameSite=Lax
```

Or:

```
Set-Cookie: session=blahblahblah; SameSite=Strict
```

"Strict" will make it so the cookie is never sent, unless the site that set the
cookie is the one in the URL bar. One problem with "Strict" is that it affects
links - if you click on a link in an email that takes you to awesomebank.com,
then SameSite=Strict cookies for awesomebank.com will not be sent, so it will
look as if the user is logged out. "Lax" makes these top-level type links work.
Ideally you'd want a one cookie for display content that was Lax, and one cookie
for API calls that was strict.

This is a fairly recent standard. According to [caniuse.com](https://caniuse.com/#feat=same-site-cookie-attribute),
currently about 92.3% of browsers support it, so this will protect the majority
of your users, but ideally you should use other forms of protection as well.

Also, if you are trying to do cross-site requests, like our example above calling
from www.awesomebank.com to api.awesomebank.com, then same-site cookies may
cause you some trouble. If you do need to do cross-domain requests like this,
in fact, you may want to set:

```
Set-Cookie: session=blahblahblah; SameSite=None
```

as future browsers may start treating a missing "SameSite" directive the
same as "Lax" by default in the near future.

## Summary

To wrap up:

* Never modify state in a GET request.
* If you can, don't accept content-types of "application/x-www-form-urlencoded", "multipart/form-data", or "text/plain".
* If you have to accept these content types, use a CSRF token or double submit
  cookie.
* If you know what origin requests are supposed to come from, check the
  origin header on the server.
* If you don't need to do cross-site requests, use SameSite cookies.
* If you need to do CORS, make sure you don't enable CORS for all origins,
  even if Stack Overflow tells you this is fine.
* Verify your site is secure with negative test cases.
