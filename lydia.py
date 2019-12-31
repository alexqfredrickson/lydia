import argparse
from models import *


def init(args):
    config = LydiaConfig()

    clean_artists_dir = args.clean_artists_dir and config.artists_directory is not None
    clean_albums_dir = args.clean_albums_dir and config.albums_directory is not None

    migrate_to_staging_dir = None
    migrate_to_albums_dir = None

    if config.staging_directory is not None and config.albums_directory is not None:
        migrate_to_staging_dir = args.migrate_to_staging_dir
        migrate_to_albums_dir = args.migrate_to_albums_dir

    if clean_artists_dir:
        clean_artists_directory(config.artists_directory, args.force)
        exit(0)

    if clean_albums_dir:
        clean_albums_directory(config.artists_directory, config.albums_directory, args.force)
        exit(0)

    if migrate_to_staging_dir:
        migrate_albums_to_staging_directory(config.albums_directory, config.staging_directory)
        exit(0)

    if migrate_to_albums_dir:
        migrate_staging_to_albums_directory(config.albums_directory, config.staging_directory)
        exit(0)


def clean_artists_directory(artists_directory, force):
    """
    Validates/cleans each folder in the artists directory, then validates artists' album directories.
    """

    print("Cleaning artists directory '{}'...\n".format(artists_directory))

    for artist_name in os.listdir(artists_directory):

        if artist_name.startswith("_"):
            print("Skipped {}!".format(artist_name))
            continue

        artist_dir = os.path.join(artists_directory, artist_name)
        artist = ArtistDirectory(artist_dir)

        if not artist.validator.is_valid:
            artist.clean(force=force)

        for album in artist.album_directories:

            if album.basename.startswith("_"):
                print("Skipped {}!".format(album.basename))
                continue

            if not album.validator.is_valid:
                album.clean(force=force)

    print("Successfully cleaned {} artists directory!".format(artists_directory))


def clean_albums_directory(artists_directory, albums_directory, force):
    """
    Validates/sanitizes each folder in the albums directory, then moves albums to the archival directory.
    """

    print("Cleaning {} albums directory...".format(albums_directory))

    for album_name in os.listdir(albums_directory):
        album = AlbumDirectory(os.path.join(albums_directory, album_name))

        if album.basename.startswith("_"):
            print("Skipped {}!".format(album.basename))
            continue
        else:
            if album.validator.is_valid:
                print("'{}' looks legit!\n".format(album_name))
            else:
                album.clean(force=force)

    print("Successfully cleaned {} albums directory!".format(albums_directory))


def migrate_albums_to_staging_directory(albums_directory, staging_directory):
    """
    Creates artist directories in the staging directory, and migrates albums into them from the albums directory.
    """

    print("Migrating {} to {}...".format(albums_directory, staging_directory))

    for album_name in os.listdir(albums_directory):
        album = AlbumDirectory(os.path.join(albums_directory, album_name))
        album.migrate(staging_directory)

    print("Successfully migrated {} to staging!".format(albums_directory))


def migrate_staging_to_albums_directory(albums_directory, staging_directory):
    """
    Moves all artists' albums in the staging directory back to the albums directory.
    """

    print("Migrating {} to {}...".format(staging_directory, albums_directory))

    for artist_dir in os.listdir(staging_directory):
        for album_dir in os.listdir(os.path.join(staging_directory, artist_dir)):
            album = AlbumDirectory(os.path.join(staging_directory, artist_dir, album_dir))
            album.move(albums_directory)

    print("Successfully migrated {} to staging!".format(staging_directory))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()

    argparser.add_argument("-a", "--clean-albums-dir", dest="clean_albums_dir", action="store_true")
    argparser.add_argument("-A", "--clean-artists-dir", dest="clean_artists_dir", action="store_true")
    argparser.add_argument("-m", "--migrate-albums-to-staging", dest="migrate_to_staging_dir", action="store_true")
    argparser.add_argument("-s", "--migrate-staging-to-albums", dest="migrate_to_albums_dir", action="store_true")
    argparser.add_argument("-M", "--migrate-to-artists-dir", dest="migrate_to_artists_dir", action="store_true")
    argparser.add_argument("-f", "--force", dest="force", action="store_true")

    args = argparser.parse_args()

    init(args)
