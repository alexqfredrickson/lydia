# lydia

**lydia** is a highly-opinionated Python 3 utility that uses a combination of regex and [eyed3](http://eyed3.nicfit.net/) in order to help tidy up your Windows .mp3 directories.

### things lydia likes

lydia **enforces artist/album naming conventions** to make your main music folder look **exactly like this**:

```properties
  joy division  # lowercase, not empty, no loose files
    ↳ 1979 - unknown pleasures # lowercase, starts with a year and hyphen, not empty
      ↳ 01 - Disorder.mp3 # "who cares"-case, is an .mp3 or .flac file (sorry .ogg/.wav!)
      ↳ 02 - Day of the Lords.mp3 
#     ↳ etc.
    ↳ 1980 - closer
#     ↳ etc.
    
  judy collins
    ↳ 1962 - golden apples of the sun
#     ↳ etc.
#   ↳ etc.
```

... and when lydia doesn't know what artist composed an album, or what year the album was produced, or what the actual album name is - lydia **takes guesses** based on regex parsing (or ID3v2 .mp3 header information) in order to suggest new album directory names.

### things lydia doesn't like

lydia *doesn't like* when your album folders contain **incomplete/orphaned files**, so she finds a new home for your orphaned .mp3 files by autogenerating artist/album folders based on ID3 metadata in tandem with the [Discogs.com API](https://www.discogs.com/developers/) ***coming soon***.

lydia will act prejudicially towards you because your album folders don't contain *all* of the .mp3 files given a particular album - and utilizes the **Discogs API** to prove it ***coming soon***.

And worst of all, lydia doesn't like the **[super hidden](http://www.eightforums.com/general-support/40071-how-stop-windows-generating-random-album-art-files.html) [files](https://hydrogenaud.io/index.php/topic,67704.0.html)** in your music folder which were generated at some point or another by Windows Media Player and just sort of fly around under the radar ***coming soon***.

### installation/setup

1. Download the lydia GitHub repository.
2. `pip install eyeD3` and `pip install discogs_client`.
3. Update the config.json file (below).
4. Let lydia loose

### config.json

The `config.json` file looks like this:

```
[
  {
    "working_directory": "I:\\Jane Doe\\Downloads",
    "archive_directory": "C:\\Jane Doe\\Music"    
  }
]
```

| name             |   type      | description  |
| :---------------- | :----------- | :------------ |
| working_directory | path      | your music downloads folder, which contains album directories for lydia to inspect |
| archive_directory | path      | your main music folder, which contains artist directories for lydia to inspect |

### coming soon

* all ***coming soon*** features

### special thanks

to winlint-cli and delia, the original C#/WPF versions of lydia that I exhumed to write this program (r.i.p.)
