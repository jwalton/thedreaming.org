---
title: "Using jscodeshift to update React text refs"
tags:
  - react
  - javascript
---

I've been meaning to learn how to use jscodeshift for a while. Today we're
going to use jscodeshift to convert some old React 15 `ref="container"`
code to some new React 16 `React.createRef()` code.

<!--more-->

I'm helping update an old React codebase to React 16. One thing that was
deprecated in React 16 was the old "string" style refs. Basically, I want
to take code that looks like this:

```js
import React from "react";

export default class MyComponent {
  render() {
    return (
      <div ref="container">
        This container is
        {` ${this.refs.container?.offsetWidth}`} pixels wide
      </div>
    );
  }
}
```

And turn it into this:

```js
import React from "react";

export default class MyComponent {
  containerRef = React.createRef();

  render() {
    return (
      <div ref={this.containerRef}>
        This container is
        {` ${this.containerRef.current?.offsetWidth}`} pixels wide
      </div>
    );
  }
}
```

Looking at this, you can _almost_ come up with some sort of regex wizardry to
make this change. But the `containerRef = React.createRef();` is not something
you're going to be able to add with any regex. We're going to needs something
stronger.

## Abstract Syntax Trees

Feel free to skip this section if you know what an "abstract syntax tree" or AST
is. This is kind of a

Let's say we have a very simple program:

```js
console.log("Hello World");
```

We want to run this program. The first thing to do is to turn this into "tokens".
What those tokens look like depend on the exact implementation of the compiler, but
here is a hypothetical tokenization of this program:

```
[
    {type: 'identifier', value: 'console'},
    {type: 'dot'},
    {type: 'identifier', value: 'log'},
    {type: 'open-brace'},
    {type: 'string-literal', value: 'Hello World'},
    {type: 'close-brace'},
    {type: 'semicolon'}
]
```

Basically we have taken out all the whitespace, and turned this into a set of
"symbols" that are meaningful to the next stage of compiling, which is turning
this program into an "abstract syntax tree". Again, the exact definition of the
AST is going to depend on the specific compiler, but if you want to check one out
from a real compiler for this program, have a look at [this link](https://astexplorer.net/#/gist/f79fed05d3fc459add2532aadc6f381a/6c64225f7963f91f7d104fd6d2ed8099fa824d45). It will look something like (this is
a bit simplified):

```
File: {
  program: {
    body: ExpressionStatement({
        expression: CallExpression({
            callee: MemberExpression({
                object: Identifier("console"),
                property: Identifier("log"),
            }),
            arguments: [
                Literal('Hello World')
            ]
        })
    })
  }
}
```

The AST is a "logical" representation of a program. The next step is to turn
this AST into some machine code so it can actually be run (although we don't
need to worry about that step, for what we're doing).

AST Explorer is an invaluable resource for looking at the output of different
compilers. You can click on the "&lt;/&gt;" icon at the top of the page to
switch to different compilers. You can even try out a jscodeshift function
by clicking on "Transform" at the top, but we're getting ahead of ourselves.

## jscodeshift to the Rescue

We're going to use a facebook library called [jscodeshift](https://github.com/facebook/jscodeshift),
which is based on a library called [recast](https://github.com/benjamn/recast).

The basic idea is, we're going to take each of our source files, parse them into
an AST, then we're going to make some changes to that tree, then we're going to
write the tree back into a javascript file.

Let's write our first codeshift script. We're going to use typescript, as
it makes writing scripts much easier.

```ts
import {
  ASTPath,
  ClassDeclaration,
  JSXAttribute,
  Transform,
  MemberExpression,
} from "jscodeshift";

export const parser = "flow";

// Convert react-15 style "text" refs into react-16 createRefs.
const transform: Transform = (fileInfo, api) => {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Do something here.

  return root.toSource();
};

export default transform;
```

We can run this with:

```sh
$ npm-run jscodeshift -t react-text-refs.ts ./sample.js -d -p
```

The "-d" will run in "dry-run mode" and not make any actual changes, and the
"-p" will print output to the screen (handy for debugging and testing).

Of course, since our script doesn't do anything, all that happens is that
jscodeshift tells us 0 files were modified.

So, let's start fixing some refs. I took a sample file and loaded it into
AST explorer so I could figure out what the AST for a JSX ref looked like.
It turns out there's a special node type called "JSXAttribute", which is awesome,
because we can just find all the JSX attributes where the name is "ref" and the
value is a sting literal:

```ts
// Convert react-15 style "text" refs into react-16 createRefs.
const transform: Transform = (fileInfo, api) => {
  const j = api.jscodeshift;
  const root = j(fileInfo.source);

  // Find all the JSX attributes of the format `ref="somestring"`.
  const refDefinitions = root.find(
    j.JSXAttribute,
    (attr: JSXAttribute) =>
      attr.name.name === "ref" && attr.value.type === "Literal"
  );

  refDefinitions.forEach((def) => {
    const { node } = def;
    const oldRefName = node.value.value;
    const newRefName = `${oldRefName}Ref`;

    // We already know this is type literal, but make typescript happy.  :)
    if (node.value.type !== "Literal") {
      return;
    }

    // TODO: Add a "somestringRef = createRef()" class property.

    // TODO: Replace `ref="somestring"` with `ref={this.somestringRef}`.

    // TODO: Find all the places where we use the ref.
  });

  return root.toSource();
};
```

Again, this doesn't do anything yet, but this makes it a little easier to break
this up and talk about each section.

## Replacing the `ref="somestring"`

The first thing we're going to talk about is the "middle" part of this function.
We're going to replace this AST node we just found with a new one:

```ts
// Replace `ref="somestring"` with `ref={this.somestringRef}`.
def.replace(
  j.jsxAttribute(
    j.jsxIdentifier("ref"),
    j.jsxExpressionContainer(
      j.memberExpression(j.thisExpression(), j.identifier(newRefName))
    )
  )
);
```

`def.replace()` will replace the node for us, but we need to build a new set
of AST nodes to replace the old one. Here we're using jscodeshift's "builder"
functions to generate a new set of nodes. It can be a little daunting to figure
out what these nodes should be. There's a handy package called
[ast-node-builder](https://github.com/rajasegar/ast-node-builder) which can give
you the jscodeshift code you need to build a given fragment of code. Or you can
write the code you want to generate into AST Explorer, and then fumble about in
VSCode with intellisense until you manage to make this work. 😛

## Adding a new property to our class

The next thing we want to do is actually add an entirely new node to the start
of our class definition. There's maybe an easier way to do this, but I wrote
a little helper function for this:

```ts
function findEnclosingClass(
  node: ASTPath
): ASTPath<ClassDeclaration> | undefined {
  let current = node.parentPath as ASTPath | undefined;
  if (!current) {
    return undefined;
  } else if (current.node.type === "ClassDeclaration") {
    return current as ASTPath<ClassDeclaration>;
  } else {
    return findEnclosingClass(current);
  }
}
```

And then we can do:

```ts
// Add a "somestringRef = createRef()" class property.
const clazz = findEnclosingClass(def);
if (!clazz) {
  console.log(`Cannot fix ref ${oldRefName} in ${fileInfo.path}`);
  return;
}

clazz.node.body.body.unshift(
  j.classProperty(
    j.identifier(newRefName),
    j.callExpression(
      j.memberExpression(j.identifier("React"), j.identifier("createRef")),
      []
    )
  )
);
```

The `body` of the class declaration is just a big array of expressions, so we can
"unshift" a new expression onto the start.

## Fixing places where refs are used

Finally, we want to find all the places where we actually use the
ref. This is actually not so trivial because there's lots of different syntax
you could use here, like:

```js
console.log(this.refs.container.offsetWidth);

const { container } = this.refs;
console.log(container.offsetWidth);

console.log(_.get(this, 'refs.container.offsetWidth');
```

These are all obviously going to generate different ASTs. I chose to just handle
the first one. This shows an example of how to chain jscodeshift commands
together:

```ts
// Find all the places where we use the ref.  Note that this doesn't fix
// *everything*, it just replaces instances of `this.refs.xxx` with
// `this.xxxRef.current`.  You may have to manually clean up other references.
root
  .find(j.MemberExpression, (node: MemberExpression) => {
    return (
      node.object.type === "MemberExpression" &&
      node.object.object.type === "ThisExpression" &&
      node.object.property.type === "Identifier" &&
      node.object.property.name === "refs" &&
      node.property.type === "Identifier" &&
      node.property.name === oldRefName
    );
  })
  .replaceWith(() =>
    j.memberExpression(
      j.memberExpression(j.thisExpression(), j.identifier(newRefName), false),
      j.identifier("current"),
      false
    )
  );
```

Since this doesn't find all occurances, I did a manual search for "this.refs"
and "refs" through my code base to make sure I'd caught everything.

## Putting it all together

If you want to see the complete version of this script you can see it
[here](https://github.com/jwalton/jscodeshift-scripts/blob/master/scripts/react-text-refs.ts).
You can run this on an entire codebase with:

```sh
$ npx jscodeshift -t scripts/react-text-refs.ts ~/dev/myproject/src
```
