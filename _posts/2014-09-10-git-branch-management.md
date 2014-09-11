---
title: "Git Gardening: Managing your Branches"
tags:
- git
---

If you are working on a large git project, it's easy to end up in git-branch hell.  Ideally people delete feature branches after they are done with them, but in practice this doesn't always happen.  Here are a few commands to help you manage your ever expanding cloud of branches.

<!--more-->

## A Note about Branches

First it's important to realize that any given branch can exist in up to three different places; there's the branch on the remote git server, there's a snapshot of the remote branch on your local machine stored in refs/remotes (e.g. 'origin/my-branch'), and there's possibly a local branch tracking the remote branch.  If someone else deletes the branch on the remote, then you will still have the other two stored on your local machine.  If you delete your local tracking branch, it also won't delete the branch from the git server automatically.

So, first, how to delete a branch everywhere:

    # Delete the branch on the remote
    git push origin --delete <branchname>

    # Delete the branch locally
    git branch -d <branchname>

## Merged Branches

Deleting merged branches is a pretty safe thing to do.  This rather lengthy series of commands will automatically delete any remote branches which have been merged (and are therefore safe to delete.)

    # Get the latest state from the origin
    git fetch --all

    # Prune branches that exist in your repo but no longer exist on origin
    git remote prune origin

    # Find all merged remote branches and make a note of them
    # in case something goes horribly wrong
    git branch -r --merged origin/master |
      grep origin |
      grep -v '>' |
      grep -v master |
      xargs -L 1 bash -c 'echo "$(git rev-parse $1) $1"' _ > delete.log

    # Find all merged remote branches and delete them
    git branch -r --merged origin/master |
      grep origin |
      grep -v '>' |
      grep -v master |
      xargs -L1 |
      awk '{sub(/origin\//,"");print}' |
      xargs git push origin --delete

    # Clean up anything local copies of branches we deleted from the origin.
    git remote prune origin

Similarly, this will delete all local branches which have been merged:

    git branch --merged master |
      grep -v master |
      xargs git branch -d

## Un-merged Branches

Un-merged branches are going to involve a little more detective work.  This command will find the most recent committer for each remote branch, and sort the results in order from the oldest commit to the most recent.  This is handy for finding ancient branches and tracking down who is responsible for them.  In my project I found some branches which were over a year old (some of them my own.)

    git for-each-ref --format='%(committerdate:raw), %(committerdate:short), %(refname:short), %(authorname) %(authoremail)' |
      sort -n |
      grep origin |
      cut -d',' -f2- |
      column -t -s ','

Finally, this handy command will give you a list of all local branches which don't have a corresponding remote branch of the same name - handy for tracking down cases where a remote branch has been deleted but you still have a local copy.  You *could* pipe this to `xargs git branch -d`, but note that if you've created a branch and not ever pushed it, this will delete that branch, so tread carefully.

    git branch -r |
      awk '{print $1}' |
      egrep -v -f /dev/fd/0 <(git branch -vv | grep origin) |
      awk '{print $1}'
