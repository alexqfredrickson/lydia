import argparse
from models import *


def init(args):
    config = LydiaConfig()

    if args.clean_archive_dir and config.archive_directory is not None:
        clean_archival_directory(config.archive_directory)

    if args.clean_working_dir and config.working_directory is not None:
        clean_working_directory(config.archive_directory, config.working_directory, args.dry_run)


def clean_archival_directory(archive_directory):
    """
    Validates and cleans each folder in the archival (artist) directorym, then validates artists' album directories.
    """

    print("Cleaning archival directory '{}'...\n".format(archive_directory))

    for artist_name in os.listdir(archive_directory):

        if artist_name.startswith("_"):
            print("Skipped {}!".format(artist_name))
            continue

        artist_dir = os.path.join(archive_directory, artist_name)
        artist = ArtistDirectory(artist_dir)

        if not artist.validator.is_valid:
            artist.clean(dry_run=args.dry_run)

        for album in artist.album_directories:

            if album.basename.startswith("_"):
                print("Skipped {}!".format(album.basename))
                continue

            if not album.validator.is_valid:
                album.clean()

    print("Successfully cleaned {} archive directory!".format(archive_directory))


def clean_working_directory(archive_directory, working_directory, dry_run=False):
    """
    Validates and cleans each folder in the working (album) directory, then moves album directories to the archival
    directory.
    """

    print("Cleaning {} working directory...".format(working_directory))

    for album_name in os.listdir(working_directory):
        album = AlbumDirectory(os.path.join(working_directory, album_name))

        if album.basename.startswith("_"):
            print("Skipped {}!".format(album.basename))
            continue
        else:
            if album.validator.is_valid:
                print("'{}' looks legit!\n".format(album_name))
            else:
                album.clean()

        if args.move_to_archive_dir:
            album.archive(archive_directory)

    print("Successfully cleaned {} working directory!".format(working_directory))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-w", "--clean-working-dir", dest="clean_working_dir", action="store_true")
    argparser.add_argument("-a", "--clean-archive-dir", dest="clean_archive_dir", action="store_true")
    argparser.add_argument("-m", "--move-to-archive-dir", dest="move_to_archive_dir", action="store_true")
    argparser.add_argument("-d", "--dry-run", dest="dry_run", action="store_true")
    args = argparser.parse_args()

    init(args)
