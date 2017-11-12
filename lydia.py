import os
from models import AlbumDirectory, Program


def init():
    program = Program()

    for working_dir_path, album_dirs, mp3_file_names in os.walk(program.working_directory):
        for album_name in album_dirs:
            album = AlbumDirectory(os.path.join(working_dir_path, album_name))

            if album.is_valid:
                print("'{}' looks legit!\n".format(album_name))
                continue
            else:
                if album.contents_are_valid is False:
                    album.lint_contents()

                if album.basename_is_valid is False:
                    album.lint_basename()

init()
