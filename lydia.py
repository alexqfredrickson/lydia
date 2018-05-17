import os
import argparse
from models import AlbumDirectory, AlbumDirectoryValidationError, LydiaConfig


def init(args):
    config = LydiaConfig()

    if args.clean_archive_dir and config.archive_directory is not None:
        pass

    if args.clean_working_dir and config.working_directory is not None:

        for working_dir_path, album_dirs, mp3_file_names in os.walk(config.working_directory):

            for album_name in album_dirs:
                album = AlbumDirectory(os.path.join(working_dir_path, album_name))

                if album.validator.is_valid:
                    print("'{}' looks legit!\n".format(album_name))

                    if args.move_to_working_directory:
                        pass
                else:
                    for error in album.validator.validation_errors:

                        if error in [AlbumDirectoryValidationError.IS_EMPTY,
                                     AlbumDirectoryValidationError.NO_MP3S_OR_FLACS]:
                            album.delete()
                            break
                        else:
                            if error == AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                                album.rename(album.basename.lower(), ask_permission=False)

                            if error == AlbumDirectoryValidationError.BASENAME_YEAR_HYPHEN_INVALID \
                                    and album.assumed_year is not None and album.assumed_title is not None:
                                album.rename("{} - {}".format(album.assumed_year, album.assumed_title))


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-w", "--clean-working-dir", dest="clean_working_dir", action="store_true")
    argparser.add_argument("-a", "--clean-archive-dir", dest="clean_archive_dir", action="store_true")
    argparser.add_argument("-m", "--move-to-archive-dir", dest="move_to_archive_dir", action="store_true")
    args = argparser.parse_args()

    init(args)
