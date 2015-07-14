---
title: Essential Plugins for Atom
tags:
- text-editor
- atom
date: '2014-09-08 20:47:00'
---
** Updated: ** See my new [list of plugins for Atom v1.0 here](http://www.thedreaming.org/2015/07/14/atom-plugins-2/).

A quick list of handy plugins I've found for the [Atom text editor](https://atom.io/).

<!--more-->

* **[chemoish/atom-valign](https://github.com/chemoish/atom-valign)** - ctrl-\ to vertically align assignments.
You can configure the hotkey in keymap.cson:

        '.editor':
            'ctrl-cmd-a': 'vertical-align:align.

* **[thomaslindstrom/color-picker](https://github.com/thomaslindstrom/color-picker)**
  - shift-cmd-c to edit HTML colors.
* **[AtomLinter/Linter](https://github.com/AtomLinter/Linter)** and
  **[AtomLinter/linter-coffeelint](https://github.com/AtomLinter/linter-coffeelint)** -
  Highlight problems in coffee-script.  Add a coffeelint.json file to your project to change settings.
* **[atom/markdown-preview](https://github.com/atom/markdown-preview)** - ctrl-shift-m to show markdown preview.
* **[kevinsawicki/monokai](https://github.com/kevinsawicki/monokai)** - The monokai color theme (should be familiar if you're a [Sublime](http://www.sublimetext.com/) user.)
* **[saschagehlich/autocomplete-plus](https://github.com/saschagehlich/autocomplete-plus)** - Autocomplete while you type.

At the moment, you should also set `editor.normalizeIndentOnPaste` to `false` if you don't want Atom to [remove your indent](https://discuss.atom.io/t/normalize-indent-on-paste-doesnt-work-as-expected/3503/5).
