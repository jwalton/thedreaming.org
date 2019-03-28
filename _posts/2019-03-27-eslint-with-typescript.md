---
title: "Use eslint with Typescript today"
tags:
- javascript
- typescript
- eslint
---

A couple of months ago Typescript team revealed that they were
[formally adopting eslint](https://eslint.org/blog/2019/01/future-typescript-eslint)
as the linter for Typescript, and that they were actively working to improve
compatibility between eslint and typescript.  What you might not know is,
you can use eslint with Typescript today!  Read more to see how to set up
eslint on your typescript project.

<!--more-->

## Vanilla Typescript Project

First of all, we need to install some dependencies:

```sh
$ npm install --save-dev eslint @typescript-eslint/parser \
    @typescript-eslint/eslint-plugin
```

`@typescript-eslint/parser` is a parser for eslint that allows eslint to parse
and understand typescript files.  `@typescript-eslint/eslint-plugin` is an eslint
plugin with some typescript specific rules.

Then you need to create your .eslintrc.js file:

```js
module.exports = {
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
        "project": "./tsconfig.json"
    },
    "extends": ["plugin:@typescript-eslint/recommended"],
};
```

And then, if your source is in the "src" folder, you can run eslint with:

```sh
$ npx eslint --ext .ts src
```

### React

If you are using react in your project, you should also
`npm install --save-dev eslint-plugin-react`, and then add
"plugin:react/recommended" to your `extends` section.  I also highly recommed
"eslint-plugin-jsx-a11y":

```js
module.exports = {
    parser: '@typescript-eslint/parser',
    parserOptions: {
        project: './tsconfig.json',
    },
    settings: {
        react: {
            version: 'detect',
        },
    },
    extends: [
        'plugin:@typescript-eslint/recommended',
        'plugin:react/recommended',
        'plugin:jsx-a11y/recommended',
    ]
};
```

To run eslint against both `.ts` and `.tsx` files:

```sh
$ npx eslint --ext .ts --ext .tsx src
```

### Prettier

If you use the `prettier` code formatter, you'll want to manually disable
all the code formatting rules, or else install `eslint-config-prettier`, and
add the following to your .eslintrc.js file:

```js
    "extends": [
        "plugin:@typescript-eslint/recommended"
        "prettier",
        "prettier/@typescript-eslint"
    ]
```

## VisualStudio Code

If you're using VisualStudio Code, you'll need to enable typescript support in the
eslint plugin in the `eslint.validate` setting.  You can do this by creating
a file called ".vscode/settings.json" in your project folder which contains:

```json
{
    "eslint.validate": [
        { "language": "typescript", "autoFix": true },
        { "language": "typescriptreact", "autoFix": true }
    ]
}
```

## Migrating from tslint

If you want to disable rules for specific files or lines, the format of the
pragmas in eslint are slightly different from tslint.  In tslint, you might
put something like this at the top of the file:

```ts
/*t slint:disable no-unused-vars */
```

The eslint equivalent would be:

```ts
/* eslint-disable @typescript-eslint/no-unused-vars */
```

Similarly, to disable tslint for a single line you might do:

```ts
// tslint:disable-next-line no-for-in-array
```

Where with eslint you would od:

```ts
// eslint-disable-next-line @typescript-eslint/no-for-in-array
```

If you're using this on an existing projects, you may want to disable some of the
"recommended" rules if they're causing too much noise, which you can do in your
eslint config file.  Here we also disable some rules specifically for files in
"/test":

```js
module.exports = {
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
        "project": "./tsconfig.json"
    },
    "extends": ["plugin:@typescript-eslint/recommended"],
    "rules": {
        "@typescript-eslint/explicit-function-return-type": "off",
        "@typescript-eslint/no-explicit-any": "off",
        // Typescript's unused variable checking is better, IMHO.
        "@typescript-eslint/no-unused-vars": "off",
    },
    overrides: [
        {
            // Disable some rules that we ruthlessly abuse in unit tests.
            files: ['test/**/*.ts', 'test/**/*.tsx'],
            rules: {
                '@typescript-eslint/no-non-null-assertion': 'off',
                '@typescript-eslint/no-object-literal-type-assertion': 'off',
            },
        },
    ],
};
```

## Mixed JS and TS Projects

If you've used eslint before, one thing you may have noticed is that, instead
of using eslint's built in "no-unused-vars", the typescript-eslint plugin
defines it's own "@typescript-eslint/no-unused-vars".  eslint works by
generating something called an "abstract syntax tree" or AST - a kind of formal
description of your source code.  When you use the "@typescript-eslint/parser"
plugin, the AST includes some extra information about types and other language
features that are not available in standard javascript.  This extra information
may trip up some eslint plugins, and some of the built in rules.

We'll probably see more and more plugins handle the typescript corner cases
in future, but for now you effectively need one configuration for js files, and
another for ts files.  Fortunately, eslint has a built in feature called
"overrides" which should make it easy to specify different rules for different
files... unfortunately at the moment you are not allowed to use an `extends`
inside an `overrides`, which means you can't easily bring in the recommended
rule set.  There's an [issue](https://github.com/eslint/eslint/issues/8813)
for getting this fixed, and [another issue](https://github.com/eslint/rfcs/pull/9)
looking at improving eslint's configuration file overall.

One solution is to use different configuration files for .ts and .js files.
Then you can do something like:

```sh
$ eslint --config ./.eslintrc-ts --ext ts
$ eslint --config ./.eslintrc-js --ext js
```

but this is hard to make work with your favorite editor.  If you have entire
subtrees that are typescript or javascript, another solution is to put a
".eslintrc.js" in each subtree, with different config; eslint will find the
"closest" configuration file (although it will keep walking up the tree, and
merge higher up configuration files with lower ones).

The solution below was suggested by [@bradzacher](https://github.com/bradzacher),
and uses the fact that eslint will let us use a .js config file.  The basic idea
is to `require` eslint-plugin's configuration, and manually merge it into
an `overrides` block to get around the `extends` limitation:

```js
// .eslintrc.js
const typescriptEslintRecommended = require('@typescript-eslint/eslint-plugin').configs.recommended;

module.exports = {
    "extends": [
        "eslint:recommended",
    ],

    "parserOptions": {
        "ecmaVersion": 8,
        "sourceType": "module",
        "ecmaFeatures": {
            "impliedStrict": true
        }
    },

    "env": {
        "node": true,
        "es6": true,
        "mocha": true
    },
    overrides: [
        {
            files: ['**/*.ts', '**/*.tsx'],
            parser: '@typescript-eslint/parser',
            parserOptions: {
                sourceType: 'module',
                project: './tsconfig.json',
            },
            plugins: [ '@typescript-eslint' ],
            rules: Object.assign(typescriptEslintRecommended.rules, {
                '@typescript-eslint/no-unused-vars': 'off',
            })
        }
    ],
};
```

This is obviously a little fragile, though.

Hopefully this helps you get set up playing with eslint on your typescript
project!