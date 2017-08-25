# lydia

**lydia** is suggest that you clean up your .mp3 folder.  More specifically, **lydia** is a highly-opinionated Python 3 utility that uses a combination of regex and [eyed3](http://eyed3.nicfit.net/) in order to help tidy things up.

### things lydia likes

lydia likes it when your .mp3 folder looks **exactly like this**:

```properties
  Joy Division # mixed-case
    ↳ 1979 - unknown pleasures # lower-case
      ↳ 01 - Disorder.mp3 # who-cares-case
      ↳ 02 - Day of the Lords.mp3 
#     ↳ etc.
    ↳ 1980 - closer
#     ↳ etc.
    
  Judy Collins
    ↳ 1962 - golden apples of the sun
#     ↳ etc.
#   ↳ etc.
```

... so lydia **enforces artist/album naming conventions** in accordance with the file system structure described above so your folder doesn't get totally out-of-whack.

And when lydia doesn't know what artist composed an album, or what year the album was produced, or what the actual album name is - lydia **take guesses** based on regex parsing, and ID3v2 metadata extracted from individual .mp3s, in order to suggest new directory names.

### things lydia doesn't like

lydia *doesn't like* when your album folders contain **incomplete/orphaned files**, so she finds a new home for your orphaned .mp3 files by autogenerating artist/album folders based on ID3 metadata in tandem with the [Discogs.com API](https://www.discogs.com/developers/) ***coming soon***.

lydia will act prejudicially towards you because your album folders don't contain *all* of the .mp3 files given a particular album - and utilizes the **Discogs API** to prove it ***coming soon***.

And worst of all, lydia doesn't like the **[super hidden](http://www.eightforums.com/general-support/40071-how-stop-windows-generating-random-album-art-files.html) [files](https://hydrogenaud.io/index.php/topic,67704.0.html)** in your music folder which were generated at some point or another by Windows Media Player and just sort of fly around under the radar ***coming soon***.

### installation/setup

1. Download the GitHub repository.
2. Download eyed3.
3. Udpate the hard-coded working directory.
4. Let lydia loose

### coming soon

* all ***coming soon*** features
* json-based config instead of hard-coded garbage:

```
[
  {
    "workingDirectory": "C:\\Jane Doe\\Music"
  }
]
```

| name             |   type      | description  |
| :---------------- | :----------- | :------------ |
| workingDirectory | string      | a path to the root-level folder that lydia inspects |

### special thanks

to winlint-cli and delia (r.i.p.) - the C# and WPF versions of lydia that I frankensteined and deprecated to write this program
