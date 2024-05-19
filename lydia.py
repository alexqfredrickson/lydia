import argparse
import json

from models import *


class ArgumentParser:
    def __init__(self):
        self.parser = argparse.ArgumentParser()

        self.parser.add_argument(
            "-a", "--clean-albums", dest="clean_albums", action="store_true", help="Cleans the albums directory."
        )

        self.parser.add_argument(
            "-A", "--clean-artists", dest="clean_artists", action="store_true", help="Cleans the artists directory."
        )

        self.parser.add_argument(
            "-s", "--stage", dest="stage", action="store_true", help="Moves albums directory to staging directory."
        )

        self.parser.add_argument(
            "-u", "--unstage", dest="unstage", action="store_true",
            help="Moves albums in staging directory to albums directory."
        )

        self.parser.add_argument("-i", "--inventory", dest="inventory", action="store_true")

        self.parser.add_argument("-f", "--force", dest="force", action="store_true")

    def parse_and_sanitize_args(self):

        config = LydiaConfig()

        args = self.parser.parse_args()

        if args.clean_albums:
            if not config.albums_directory:
                print("ERROR: An albums directory must be specified in lydia's `config.json` file..")
                exit(1)

            if not config.album_validation_behavior \
                    or not config.album_validation_behavior["rename_as_lowercase"] \
                    or not config.album_validation_behavior["rename_as_year_plus_title"] \
                    or not config.album_validation_behavior["remove_empty_folders"] \
                    or not config.album_validation_behavior["remove_folders_with_no_mp3s_or_flacs"]:

                print("ERROR: Album validation behavior must be specified in lydia's `config.json` file.")
                exit(1)

        if args.clean_artists:
            if not config.artists_directory:
                print("ERROR: An artists directory must be specified in lydia's `config.json` file..")
                exit(1)

        if args.stage or args.unstage:
            if not config.staging_directory:
                print("ERROR: A staging directory must be specified in lydia's `config.json` file.")
                exit(1)

        if args.inventory:
            if not config.inventory_path:
                print("ERROR: An inventory path must be specified in lydia's `config.json` file.")
                exit(1)

        return args


class Lydia:
    def __init__(self):
        self.config = LydiaConfig()

    def init(self, args):

        if args.clean_artists:
            self.clean_artists_directory(args.force)

        if args.clean_albums:
            self.clean_albums_directory()

        if args.stage:
            self.migrate_albums_to_staging_directory()

        if args.unstage:
            self.migrate_staging_to_albums_directory()

        if args.inventory:
            self.create_inventory()

    def clean_artists_directory(self, force):
        """
        Validates/cleans each folder in the artists directory, then validates artists' album directories.
        """

        artists_dir = self.config.artists_directory

        print(f"Cleaning '{artists_dir}'...\n")

        artist_directories = [ArtistDirectory(os.path.join(artists_dir, a)) for a in os.listdir(artists_dir)]

        for artist in artist_directories:

            if artist.basename.startswith("_"):
                print(f"Skipped {artist.basename}.")
                continue

            if not artist.validator.is_valid:
                artist.clean(force=force)

            for album in artist.album_directories:

                if album.basename.startswith("_"):
                    print(f"Skipped {album.basename}!")
                    continue

                if not album.validator.is_valid:
                    album.clean(force=force)

        print(f"Successfully cleaned {artists_dir}.")

    def clean_albums_directory(self):
        """
        Validates/sanitizes each folder in the albums directory, then moves albums to the archival directory.
        """

        albums_dir = self.config.albums_directory

        print(f"Cleaning {albums_dir}...")

        for album_name in os.listdir(albums_dir):
            album = AlbumDirectory(os.path.join(albums_dir, album_name))

            if album.basename.startswith("_"):
                print(f"Skipped {album.basename} due to leading underscores in album name...")
                continue

            album.clean()

        print(f"Successfully cleaned {albums_dir}.")

    def migrate_albums_to_staging_directory(self):
        """
        Creates artist directories in the staging directory, and migrates albums into them from the albums directory.
        """

        albums_dir = self.config.albums_directory
        staging_dir = self.config.staging_directory

        print(f"Migrating {albums_dir} to {staging_dir}...")

        for album_name in os.listdir(albums_dir):
            album = AlbumDirectory(os.path.join(albums_dir, album_name))
            album.migrate(staging_dir)

        print(f"Successfully migrated {albums_dir} to {staging_dir}.")

    def migrate_staging_to_albums_directory(self):
        """
        Moves all artists' albums in the staging directory back to the albums directory.
        """

        albums_dir = self.config.albums_directory
        staging_dir = self.config.staging_directory

        print(f"Migrating {staging_dir} to {albums_dir}...")

        for artist_dir in os.listdir(staging_dir):
            for album_dir in os.listdir(os.path.join(staging_dir, artist_dir)):
                album = AlbumDirectory(os.path.join(staging_dir, artist_dir, album_dir))
                album.move(albums_dir)

        print(f"Successfully migrated {staging_dir} to {albums_dir}.")

    def create_inventory(self):
        print("INFO: Creating inventory from base artist directory ...")

        artist_inventory = {}

        artist_dirs = [
            ArtistDirectory(os.path.join(self.config.artists_directory, a), validate=False, parse_mp3s=False)
            for a in os.listdir(self.config.artists_directory)
        ]

        for artist in artist_dirs:
            try:
                artist_inventory[artist.basename] = [album.basename for album in artist.album_directories]
            except TypeError as e:
                print(e)

        with open(os.path.join(self.config.inventory_path, "artists.json"), 'w', encoding='utf-8') as f:
            json.dump(artist_inventory, f, indent=4)

        print("INFO: Creating inventory from base albums directory ...")
        album_inventory = []

        album_dirs = [
            AlbumDirectory(os.path.join(self.config.albums_directory, a), validate=False)
            for a in os.listdir(self.config.albums_directory)
        ]

        for album in album_dirs:
            album_inventory.append(album.basename)

        with open(os.path.join(self.config.inventory_path, "albums.json"), 'w', encoding='utf-8') as f:
            json.dump(album_inventory, f, indent=4)


if __name__ == "__main__":
    Lydia().init(ArgumentParser().parse_and_sanitize_args())
