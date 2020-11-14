# lydia (v1.0.0-beta)

**lydia** is a somewhat-opinionated Python 3 utility that helps you tidy up your Windows .mp3 directories.
 
#### things lydia likes

lydia enforces artist/album naming conventions to make your music folder look **exactly like this**:

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

... and when lydia doesn't know what artist composed an album, or what year the album was produced, or what the actual album name is - lydia **guesses** based on regex parsing and ID3v2 .mp3 header information (using [eyed3](http://eyed3.nicfit.net/)) in order to suggest new album directory names.

## installation & configuration

1. Clone this repository.
2. Install the dependencies located in the `requirements.txt` file.
3. Create a config.json file at the project root:

```
[
  {
    "albums_directory": "I:\\Jane Doe\\Downloads",
    "artists_directory": "C:\\Jane Doe\\MusicArchive",
    "staging_directory": "C:\\Jane Doe\\StagingArchive",
  }
]
```

| name               | type   | description                                              |
| :----------------  | :----- | :--------------------------------------------            |
| albums_directory   | string | the path to some downloads folder that contains albums   |
| artists_directory  | string | the path to some archival folder that contains artists   |
| staging_directory  | string | a mock 'artists_directory' used for staging/dry runs |


#### usage

run `lydia.py -help` for usage

#### errata

 by convention, lydia will skip validation of any artist/album directories with leading underscores

#### special thanks

to winlint-cli and delia (the original C#/WPF versions of lydia; r.i.p.)
