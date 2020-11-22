---
title: "Organizing music with Musicbrainz Picard"
tags:
  - DNS
  - Synology
  - Crypto
---

I've spent some time playing with a couple of different tools for organizing my MP3 collection.  If you have a large music collection, you probably have some old songs in there you ripped from CDs, and they might have some metadata that's not quite up-to-snuff.  There's probably some spelling mistakes in there, and maybe you have some files where the artist is "Blink 182" and some are "blink-182" - things like this.  What we want is some automated way of fixing all this metadata, and sorting files into the correct folder based on their metadata.  [Beets](http://beets.io/) is very popular program for this, but it's not being actively maintained.  [MusicBrainz Picard](https://picard.musicbrainz.org) has a nice UI and is pretty easy to use.

<!--more-->

## Backup

Before we start, we're using some software which is going to automatically overwrite data in files and move files around on disk.  This would be a really good time to make a backup of your whole music library.

## MusicBrainz Picard

In Preferences, I set up the following:

Under "Metadata", check "Translate artist names to this locale where possible" (I have some Japanese artists in my collection, such as Yoko Kanno, and while I can recognize their Japanese names in context, I wouldn't want to try to type one into a searchbox.)

Under "Cover Art", I enabled "Embed cover images into tags" and "Save cover images as separate files" (lots of apps like to see a "cover.jpg" file in the save folder as the album) and then I checked all the "Cover Art Providers".

Under "Fingerprinting" I clicked on the "Get API Key...".  Most of my music was purchased on iTunes, but I have some very old MP3s from the pre-iTunes days which don't have any metadata, so I can use Picard to look them up based on their music fingerprint, similar to how apps like SoundHound or Shazam work.

Under "File Naming" I selected "Move files when saving" and "Move additional files".  I set "Move additional files" to be "\*.jpg \*.png \*.pdf" (so it will move album covers and liner notes when I move a track - notice this means you should *not* try to move a file out of Downloads directly with Picard - it will end up moving whatever random jpgs and pdfs you have in your downloads folder.)  I'm going to make a full copy of my music library into a folder called "to-sort" and open this in Picard, and every time I save a file in Picard, I want it to move it to the destination directory "music" (ultimately we want this "music" directory to be the one that Navidrome reads from, so ideally this is a network share on the device we're going to run navidrome on).  I used this as my naming script:

```
$if($eq(%compilation%,1),Compilations,$if2(%albumartist%,%artist%,Unknown Artist))/
$if(%albumartist%,%album%/,Unknown Album/)
$if($gt(%totaldiscs%,1),%discnumber%-,)$if($and(%albumartist%,%tracknumber%),$num(%tracknumber%,2) ,)$if(%_multiartist%,%artist% - ,)%title%
```

You can read the [MusicBrainz scripting documentation](https://picard-docs.musicbrainz.org/en/scripting.html), or check out their [forum](https://community.metabrainz.org/t/repository-for-neat-file-name-string-patterns-and-tagger-script-snippets/2786/) for pre-built scripts (some people get a little crazy with their scripts).

There are quite a few [plugins](https://picard.musicbrainz.org/plugins/) available if Picard doesn't do something you need it to do.

Once you have Picard all set up, click "Add Folder", and add some music from your "to-sort" folder (I prefer not to add the whole thing at once - I'll add about 10-20 albums or so at a time).  Click on "Unclusterd Files" and then the "Cluster" icon at the top to sort them into groups based on album (careful - if you have a bunch of MP3s where the album is "Unknown", they'll all get lumped together).  Then, pick the songs or albums you want to find and click the "Lookup" button to look up your music - this will move music into albums on the right hand side.

You can click on individual tracks to see exactly what Picard is going to change.  If Picard gets something wrong, you can either click the track to manually edit it, or if it gets entirely the wrong album you can search for an album in the box at the top, and then drag-and-drop tracks into the correct album.  When you drag-and-drop a track, you can drag it to the album title to get Picard to figure out where it should go, or you can drag-and-drop it to the specific track in the Album.  Click the album and click the "Save" icon to write the entire album to disk, and move it to the correct spot.

You can also pick unsorted tracks on the left hand side, and edit their metadata and click "Save" to write updates and move them on disc - sometimes MusicBrainz just doesn't have the release you're looking for.

## Organizing our Music with Beets

If you want to try out Beets, this is what I did to get it set up.  Using Beets requires some proficiency with the command line, and you should know how to install software like python or ffmpeg.  Note that as of this writing, the latest published version of Beets doesn't work with the latest version of Python, and since Beets hasn't seen a new release in about a year, this means we're not likely to see a new one soon.  So, if you want to go this route, you have to install Beets from `master` - the very latest copy, which may have some weird bugs.

```sh
pip3 install https://github.com/beetbox/beets/tarball/master requests
# If you want to use the `lastgenre` plugin:
pip3 install lastgenre
# If you want to use the `lyrics` plugin:
pip3 install requests
```

Now create a file call `.config/beets/config.yaml` and put this in it:

```yaml
# This is where your music will end up after being processed
directory: ~/music

# This is where beets will store it's db
library: ~/.config/beets/musiclibrary.db

import:
  # Copy music to ~/music.  Change to `move: yes` to move.
  copy: yes
  # Write updates to the music when it is imported.
  write: yes

# Automatically get art, lyrics, and fix genre
plugins: fetchart lyrics lastgenre

# How music will be written to disk.
# See https://beets.readthedocs.io/en/stable/reference/config.html#path-format-config
paths:
    default: $albumartist/$album%aunique{}/$track $title
    singleton: $artist/Non-Album/$title
    comp: Compilations/$album%aunique{}/$track $title
```

Beets will try to find cover art for albums from the Internet, but if you want a specific image for an album, you can save it as a `cover.jpg` file in the same folder as the album, and beets will pick it up.  If you find beets gets some weird image that you weren't expecting, you can extract the image from an MP3 file with ffmpeg:

```sh
ffmpeg -i file.mp3 cover.jpg
```

(There's an [open PR for beets](https://github.com/beetbox/beets/pull/3580) which makes it so beets can extract cover art from your music files automatically.)

And now we can start importing music:

```sh
beet import /path/to/your/music
```

This can take a while, and beets is going to ask you a lot of questions.  You can read the details of [how to answer them here](https://beets.readthedocs.io/en/stable/guides/tagger.html).
