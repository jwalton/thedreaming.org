---
title: "'import' vs 'import *' in Babel"
tags:
- javascript
- babel
- es6
- modules
---

If you're using ES6 in node.js, there's a lot of reasons to use the new "import" keyword to import modules:

```js
import ld from 'lodash'; // Yay!
const ld = require('lodash'); // Boo!
```

The old "require" way of doing things is known as "CommonJS".  The new "import" way of doing things is known as "ES6 Modules".  One of the things you've probably noticed, though, is you can use the "import * as" vs "import", and sometimes it seems to makes a difference, and sometimes it doesn't:

```js
import ld from 'lodash';
import * as ld from 'lodash';
```

So, what's the difference between these?  Which one is "right"?

<!--more-->

If all our code is written using ES6 modules, you can export individual functions or objects, or you can export a "default" (or you can do both!):

```js
// foo.js
export function hello() {console.log('hello');}
export default function() {console.log('default');}
```

How you access these depends on how you import them:

```js
// user1.js
import foo from './foo';
foo(); // prints "default"
foo.hello(); // Doesn't work - `foo` is the second function
             // from foo.js, which doesn't have a 'hello' property.

// user2.js
import * as foo from './foo';
foo(); // Can't do this - foo is an object.
foo.hello(); // Prints 'hello'
foo.default(); // Prints 'default'
```

Now, this is all well and good in "pure ES6 Modules" land, but things start getting interesting when you mix modules and CommonJS.  What happens if we rewrite foo.js to look like this:

```js
// foo.js
modules.exports = function() {console.log('default');}
modules.exports.default = function() {console.log('default2');}
modules.exports.hello = function() {console.log('hello');}
```

ES6 Modules are defined in the "ECMAScript 2015 Language Specification", which doesn't mention "CommonJS" once.  So how these interoperate depends on your build environment.  If you're using Babel to transpile your ES6 code, then it's up to Babel to decide how to make this happen.  One day when Node.js supports ES6 Modules natively, it'll be up to Node.js to decide how they interoperate, but hopefully they'll take their queues from Babel.

So, if you try out our above example:

```js
// user1.js
import foo from './foo';
foo(); // Prints 'default'
foo.hello(); // Prints 'hello'
foo.default(); // Prints 'default2'

// user2.js
import * as foo from './foo';
foo(); // Doesn't work - foo is not a function.
foo.hello(); // Prints 'hello'
foo.default(); // Prints 'default'
```

`foo.hello()` works exactly the same in both cases.  The no-asterisk version probably behaves closest to what you'd expect to happen when if comes to handling `default`.  For most modules, though, which don't set modules.exports (and don't export a function named `default`), they're going to behave the same...  Well, almost.  Let's have a look at the compiled code that Babel generates:

```js
// user1.js
var _foo = require('./foo');
var _foo2 = _interopRequireDefault(_foo);
function _interopRequireDefault(obj) {
    return obj && obj.__esModule ? obj : { default: obj };
}
(0, _foo2.default)();
_foo2.default.hello();
_foo2.default.default();


// user2.js
var _foo = require('./foo');
var foo = _interopRequireWildcard(_foo);
function _interopRequireWildcard(obj) {
    if (obj && obj.__esModule) {
        return obj;
    } else {
        var newObj = {};
        if (obj != null) {
            for (var key in obj) {
                if (Object.prototype.hasOwnProperty.call(obj, key))
                    newObj[key] = obj[key];
            }
        }
        newObj.default = obj;
        return newObj;
    }
}

foo();
foo.hello();
foo.default();
```

Wow!  There's a lot going on in that second file!  The first one just returns the object from the module, wrapped in a `{default}` object.  The second one creates a whole new object and copies all the properties from our module into it.  This has some important ramifications.  Let's say you have a circular dependency (where module A requires module B, and module B imports module A).  Node.js is going to make this work for you by filling in all the exports in one of these two modules first, and then going back and filling in the exports in the second one later.  If you `console.log(Object.keys(B))` at the top level in A, then depending on the order things get pulled in, this might print out all the functions on B, or it might print nothing.  If your're using the asterisk-version of import, this means you might copy all the functions out of B, or you might end up with an empty module.

Also, if you're a fan of unit test frameworks that stub out functions, such as `sinon`, you're going to find you can't stub functions in your CommonJS module if it was imported with the asterisk, but you can if it was imported directly - again, this is because `sinon` is going to stub out functions on the module, but the asterisk-import has already copied all the function out of that module into it's own private object.

So, in general, when you're calling from ES6 code to CommonJS code, prefer the no-star version.  The only downside to this is, if you later go back and rewrite 'foo.js' to use ES6 modules, then you'll either have to find all the code that requires it and add the star in (fortunately `eslint-plugin-import` can help you find such problems if you don't have a `default` export, since it will complain that you're trying to import default from a module with no default export).
