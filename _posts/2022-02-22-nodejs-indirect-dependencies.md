---
title: "Node.JS: Upgrading indirect dependencies"
tags:
  - node.js
  - npm
---

You want to install an npm package - let's say `amqp-connection-manager`.  This particular package has a dependency on another package called `promise-breaker`, so when you install `ampq-connection-manager`, `promise-breaker` gets installed automatically (although you won't see it in your package.json).  Now let's suppose there's a security vulnerability in promise-breaker.  You want to upgrade promise-breaker, but it isn't even in your package.json!  How do you go about doing this?

<!--more-->

## SemVer

First, a quick explanation of "semantic versioning".  Node.js packages have version numbers like "5.3.2".  Here "5" is called the major version, "3" is the minor version, and "2" is the patch version.  When a new version of a package comes out, it should increment the major version if there are breaking changes.  If not, it should upgrade the minor version if there are new features, or the patch version if there are only bug fixes.  This means you know it should be reasonably safe to upgrade from 5.3.2 to 5.3.3 (since this only contains bug fixes) or to 5.4.0 (which has some new features, and maybe some bug fixes) but upgrading to 6.0.0 means breaking changes and you'll probably have to do some work to do that upgrade.  "0.x.y" versions are special; here the "x" is usually treated as the major version, and the "y" as the "minor/patch" version.

If you peer into the [package.json for amqp-connection-manager](https://github.com/jwalton/node-amqp-connection-manager/blob/890497dd54587f6ad4e4f082fd956baa31de3cbf/package.json#L19), you'll see that it relies on:

```json
  "dependencies": {
        "promise-breaker": "^5.0.0"
  }
```

Notice the `^` (called a "caret") - this is important! The [caret](https://docs.npmjs.com/cli/v6/using-npm/semver#caret-ranges-123-025-004) means that this package relies on 5.0.0, or any version higher than 5.0.0 with a "5" in the major version number.  This means if you already have promise-breaker 5.1.0 installed when you try to install amqp-connection-manager, npm won't install 5.0.0, it will just use the 5.1.0 you already have installed.  And, this also means if a new 5.x.x version of promise-breaker comes out, you can upgrade to it without upgrading amqp-connection-manager.

The caret also correctly interprets versions with a leading 0 - `^0.1.2` means this depends on 0.1.x for any x >= 2.  Sometimes you will also see [tilde ranges](https://docs.npmjs.com/cli/v6/using-npm/semver#tilde-ranges-123-12-1) like `~5.2.1`.  These are very similar to caret ranges - in most cases you can use them interchangably.

If you find a package that doesn't have a caret or tilde range, for example if you find a package that contains something like:

```json
  "dependencies": {
        "promise-breaker": "5.0.0"
  }
```

Then you're in trouble.  There's ways to force npm or yarn to upgrade to a higher version, but the best way to resolve this is to raise a PR against the package that's importing promise-breaker, and get them to upgrade (and preferably get them to replace "5.0.0" with caret or tilde range).

## Upgrading with npm

So, back to our original example - you installed ampq-connection-manager, and you want to upgrade it's dependency promise-breaker.  promise-breaker will not be in your package.json, but you might notice that it is in your package-lock.json.  If you `rm -rf node_modules` and `npm install`, then npm will just reinstall the old version of promise-breaker, because that's what's in your lock file.

Before doing anything else, make sure you've upgraded to the latest version of npm, because the `upgrade` command in npm has been notoriously buggy in the past:

```sh
$ npm install -g npm
```

If you need to upgrade promise-breaker because of a security problem from `npm audit`, you can `npm audit fix`, which will try to automatically fix call security problems.  This may upgrade other libraries too.

If you know that you want to upgrade a direct dependency of one of your dependencies, then the command you want to run is:

```sh
$ npm upgrade --depth 2 promise-breaker
```

This will search through your package-lock.json for packages named "promise-breaker" to upgrade, but it will only do your direct dependencies (at depth 1) and their direct dependencies (at depth 2).  If you depend on a library that depends on amqp-connection-manager, then promise-breaker would be at `--depth 3`.  You can figure this out by running `npm ls promise-breaker`, which will show you how far down the dependency tree promise-breaker is.  On small projects you might be able to get away with something like `npm upgrade --depth 999 promise-breaker`, but you might find this a bit slow on larger projects.

If `npm upgrade --depth ...` doesn't work for you (which it sometimes doesn't - notoriously buggy, and sometimes for whatever reason you have to use an older version of npm) then there are a few other options you can try here.  You can `npm uninstall amqp-connection-manager && npm install amqp-connection-manager` - this will often fix the problem.  You can also `npm install promise-breaker@5.2.0 && npm uninstall promise-breaker`, which will force it up to 5.2.0 and then remove it from package.json.  The "nuclear option" is `rm -rf node_modules package-lock.json && npm install`, which will regenerate your package-lock.json from scratch, although this may upgrade several other libraries in the process.

## Upgrading with Yarn

Yarn makes this a little easier - if you run:

```sh
$ yarn upgrade amqp-connection-manager
```

will upgrade amqp-connection-manager to the latest version (matching semver) and all it's dependencies.  Note that if you run `yarn upgrade promise-breaker`, this won't do what you want it to - you need to know the pacakge that includes promise-breaker.  The easiest way to figure this out is with:

```sh
$ yarn why promise-breaker
```

which will tell you why the dependency is in your dependency tree.

Happy upgrading!