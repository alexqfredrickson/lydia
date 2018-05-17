import os
import argparse
from models import AlbumDirectory, AlbumDirectoryValidationError, LydiaConfig


def init(args):
    config = LydiaConfig()

    for working_dir_path, album_dirs, mp3_file_names in os.walk(config.working_directory):
        for album_name in album_dirs:
            album = AlbumDirectory(os.path.join(working_dir_path, album_name))

            if album.validator.is_valid:
                print("'{}' looks legit!\n".format(album_name))
                continue
            else:
                for error in album.validator.validation_errors:

                    if error in [AlbumDirectoryValidationError.IS_EMPTY,
                                 AlbumDirectoryValidationError.NO_MP3S_OR_FLACS]:
                        album.delete()
                        break

                    if error == AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                        album.rename(album.basename.lower(), ask_permission=False)

                    if error == AlbumDirectoryValidationError.BASENAME_YEAR_HYPHEN_INVALID \
                            and album.assumed_year is not None and album.assumed_title is not None:
                        album.rename("{} - {}".format(album.assumed_year, album.assumed_title))


if __name__ == "__main__":
    args = argparse.ArgumentParser().parse_args()
    init(args)
