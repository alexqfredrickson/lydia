import os
from models import *


def unstage_albums_back_to_working_directory(staging_dirpath):
    config = LydiaConfig()

    for artist_dir in os.listdir(staging_dirpath):
        for album_dir in os.listdir(os.path.join(staging_dirpath, artist_dir)):
            album = AlbumDirectory(os.path.join(staging_dirpath, artist_dir, album_dir))
            album.move(config.working_directory)
