---
title: "Setting up Jest unit tests in a React + Typescript project"
tags:
  - node.je
  - typescript
---

Here's what I do when I want to set up a Jest on a React project.

<!--more-->

First, we need to install some dependencies:

```sh
npm install --save-dev jest babel-jest ts-jest chai chai-jest identity-obj-proxy
```

What are all of these?

- `jest` is a unit test runner from Facebook. You probably already know this, because you're reading this.
- `ts-jest` is a `transform` for jest which compiles typescript files. If you're using babel to compile your typescript files, you can skip this.
- `babel-jest` is like `ts-jest`, but uses babel to transform files - handy if you have a project with some mixed typescript and javascript.
- `chai` is an assertion library. Jest already comes with an `expect` built in, but if you're coming from mocha you probably already use chai, and it's somewhat more expressive and has a lot of plugins available.
- `chai-jest` is a plugin for chai which has supports jest mocks. It basically re-implements a bunch of the jest-specific asserts on the built-in `expect` object. See the [documentation](https://github.com/jwalton/chai-jest#readme) for a list of assertions available.
- `identity-obj-proxy` is a handy library for cases where we import files like CSS
  modules. If you `import styles from 'styles.css'`, then we can configure jest
  to import 'identity-obj-proxy' for \*.css, and then when you do `styles.container`,
  it will resolve to "container" instead of throwing an exception.

Then we're going to create some files to set up jest. First, jest.config.js:

```js
// jest.config.js
module.exports = {
  globals: {
    "ts-jest": {
      // Tell ts-jest about our typescript config.
      // You can specify a path to your tsconfig.json file,
      // but since we're compiling specifically for node here,
      // this works too.
      tsConfig: {
        target: "es2019",
      },
    },
  },
  // Transforms tell jest how to process our non-javascript files.
  // Here we're using babel for .js and .jsx files, and ts-jest for
  // .ts and .tsx files.  You *can* just use babel-jest for both, if
  // you already have babel set up to compile typescript files.
  transform: {
    "^.+\\.jsx?$": "babel-jest",
    "^.+\\.tsx?$": "ts-jest",
    // If you're using babel for both:
    // "^.+\\.[jt]sx?$": "babel-jest",
  },
  // In webpack projects, we often allow importing things like css files or jpg
  // files, and let a webpack loader plugin take care of loading these resources.
  // In a unit test, though, we're running in node.js which doesn't know how
  // to import these, so this tells jest what to do for these.
  moduleNameMapper: {
    // Resolve .css and similar files to identity-obj-proxy instead.
    ".+\\.(css|styl|less|sass|scss)$": `identity-obj-proxy`,
    // Resolve .jpg and similar files to __mocks__/file-mock.js
    ".+\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$": `<rootDir>/__mocks__/file-mock.js`,
  },
  // Tells Jest what folders to ignore for tests
  testPathIgnorePatterns: [`node_modules`, `\\.cache`],
  testURL: `http://localhost`,
};
```

We need to create the "**mocks**/file-mock.js" referenced above in "moduleNameMapper", too. This file will be imported in place of ".jpg" or ".mp3" or similar files:

```js
// __mocks__/file-mock.js
module.exports = "test-file-stub";
```

## Resolving Custom Paths

In your tsconfig.json file, you can set up a "paths" section:

```json
"paths": {
    "components/*": ["src/components/*"],
}
```

This lets you `import Button from "components/Button"`, and helps you avoid long chains of "../../.." in your code. But, we need to make jest know about these imports. The easiest way to do this, if you're already using webpack, is via the jest-webpack-resolver. In your webpack configuration, you probably already have something like:

```js
const TsconfigPathsPlugin = require('tsconfig-paths-webpack-plugin');

module.exports = {
    ...
    resolve: {
        modules: ['node_modules'],
        plugins: [new TsconfigPathsPlugin({ extensions })],
        extensions: ['.js', '.jsx', '.ts', '.tsx'],
    },
    ...
}
```

So we're going to take advantage of the fact that webpack knows how to resolve things already:

```sh
npm install --save-dev jest-webpack-resolver
```

And then somewhere in your jest.config.js add:

```js
module.exports = {
    ...
    resolver: 'jest-webpack-resolver',
    ...
}
```

If you are not using webpack, then check out [tsconfig-paths-jest](https://www.npmjs.com/package/tsconfig-paths-jest) as a possible alternative.

## Running tests

At this point you should be able to:

```sh
npx jest
```

And it should run your tests!

## Example Test File

Here's a quick example of a test file - if you have a `Button.tsx`, you might put this in `Button.test.tsx` in the same folder.  Note that this uses the `@testing-library/react` and `@testing-library/user-event` libraries:

```ts
import { render } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import React from "react";
import chai from "chai";
import chaiDom from "chai-dom";

chai.use(chaiDom);
const { expect } = chai;

describe("Test Suite", () => {
  beforeEach(() => {
    // TODO: Uncomment this if you're using `jest.spyOn()` to restore mocks between tests
    // jest.restoreAllMocks();
  });

  it("click on a button", () => {
    const { getByText } = render(<button>Hello World</button>);

    // `getByText` comes from `testing-library/react` and will find an element,
    // or error if the element doesn't exist.  See the queries documentation
    // for info about other query types:
    // https://testing-library.com/docs/dom-testing-library/api-queries
    const button = getByText("Hello World");

    // `userEvent` is a library for interacting with elements.  This will
    // automatically call `React.act()` for you - https://reactjs.org/docs/test-utils.html#act.
    userEvent.click(button);
  });
});
```

Note that all tests run in node.js, where this is no browser.  By default, Jest will initialize a [`jsdom`](https://github.com/jsdom/jsdom) environment for you, which gives you a `window` and a `document` and will let you render nodes to a virtual screen.  But, if you're writing a test for a module that doesn't need to interact with the DOM, you can speed up a test by using the "node" jest environment which will skip all of that:

```ts
/**
 * @jest-environment node
 */

import chai from "chai";
import chaiJest from "chai-jest";
chai.use(chaiJest);

const { expect } = chai;

describe("Test Suite", () => {
  it("should do the thing", () => {
    // TODO
  });
});
```
