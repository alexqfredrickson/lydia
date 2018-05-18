import argparse
from models import *


def init(args):
    config = LydiaConfig()

    if args.clean_archive_dir and config.archive_directory is not None:
        print("Cleaning archival directory '{}'...\n".format(config.archive_directory))

        for artist_name in os.listdir(config.archive_directory):

            if artist_name.startswith("_"):
                print("Skipped {}!".format(artist_name))
                continue

            artist_dir = os.path.join(config.archive_directory, artist_name)
            artist = ArtistDirectory(artist_dir)

            if not artist.validator.is_valid:
                artist.clean(dry_run=args.dry_run)

            for album in artist.album_directories:
                if not album.validator.is_valid:
                    album.clean()

        print("Successfully cleaned {} archive directory!".format(config.archive_directory))

    if args.clean_working_dir and config.working_directory is not None:
        print("Cleaning {} working directory...".format(config.working_directory))

        for album_name in os.listdir(config.working_directory):
            album = AlbumDirectory(os.path.join(config.working_directory, album_name))

            if album.validator.is_valid:
                print("'{}' looks legit!\n".format(album_name))

                if args.move_to_archive_dir:
                    pass
            else:
                album.clean()

        print("Successfully cleaned {} working directory!".format(config.archive_directory))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-w", "--clean-working-dir", dest="clean_working_dir", action="store_true")
    argparser.add_argument("-a", "--clean-archive-dir", dest="clean_archive_dir", action="store_true")
    argparser.add_argument("-m", "--move-to-archive-dir", dest="move_to_archive_dir", action="store_true")
    argparser.add_argument("-d", "--dry-run", dest="dry_run", action="store_true")
    args = argparser.parse_args()

    init(args)
