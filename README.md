# lydia (v1.0.0-beta)

**lydia** is a somewhat-opinionated Python 3 utility that helps you tidy up your Windows .mp3 directories.
 
#### things lydia likes

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

... and when lydia doesn't know what artist composed an album, or what year the album was produced, or what the actual album name is - lydia **takes guesses** based on regex parsing and ID3v2 .mp3 header information (using [eyed3](http://eyed3.nicfit.net/)) in order to suggest new album directory names.

#### things lydia doesn't like

lydia *doesn't like* when your album folders contain **incomplete/orphaned files**, so she finds a new home for your orphaned .mp3 files by autogenerating artist/album folders based on ID3 metadata in tandem with the [Discogs.com API](https://www.discogs.com/developers/) ***coming soon***.

lydia will act prejudicially towards you because your album folders don't contain *all* of the .mp3 files given a particular album - and utilizes the **Discogs API** to prove it ***coming soon***.

And worst of all, lydia doesn't like the **[super hidden](http://www.eightforums.com/general-support/40071-how-stop-windows-generating-random-album-art-files.html) [files](https://hydrogenaud.io/index.php/topic,67704.0.html)** in your music folder which were generated at some point or another by Windows Media Player and just sort of fly around under the radar ***coming soon***.

## installation/setup

1. Clone this repository.
2. Install the dependencies located in the `requirements.txt` file.
3. Create a config.json file at the project root:

```
[
  {
    "albums_directory": "I:\\Jane Doe\\Downloads",
    "artists_directory": "C:\\Jane Doe\\MusicArchive",
    "staging_directory": "C:\\Jane Doe\\StagingArchive",
    "discogs_user_token": "abc123" (coming soon)
  }
]
```

| name               | type   | description                                              |
| :----------------  | :----- | :--------------------------------------------            |
| albums_directory   | string | the path to some (downloads) folder, containing albums   |
| artists_directory  | string | the path to some (archival) folder, containing artists   |
| staging_directory  | string | same as artists_directory, but used for staging/dry runs |
| discogs_user_token | string | a discogs api user token (coming soon)                   |


And have fun!

## usage

| cli args                         | details                                                      |
| :--------                        | :---------------------------------------------               |
| -a, --clean-albums-dir           | cleans up the albums directory                               |
| -A, --clean-artists-dir          | cleans up the artists directory AND cleans up albums         |
| -m, --migrate-albums-to-staging  | migrates albums to staging directory                         |
| -s, --migrate-staging-to-albums  | unmigrates albums from staging directory to albums directory |
| -M, --migrate-to-artists-dir     | migrates albums to artists directory (***coming soon***)     | 
| -f, --force                      | anti-paranoid mode                                           |

#### errata

 * by convention, lydia will skip validation of any artist/album directories with leading underscores.

#### coming soon

* all ***coming soon*** features

#### special thanks

to winlint-cli and delia (the original C#/WPF versions of lydia; r.i.p.)
