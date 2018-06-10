import warnings
import discogs_client
from models import LydiaConfig


class Discogs:
    def __init__(self):
        self.controller = discogs_client.Client(
            'lydia/0.0.1-alpha',
            user_token=LydiaConfig().discogs_user_token
        )

    @staticmethod
    def search_artist(artist_name):
        artist_results = discogs.controller.search(artist_name, type='artist')

        if len(artist_results) > 1:
            warnings.warn(message="The Discogs search for artist '{}' returned multiple artists: {}"
                          .format(artist_name, ", ".join([a.name for a in artist_results])))
        elif len(artist_results) == 0:
            warnings.warn(message="The Discogs search for artist '{}' returned no results."
                          .format(artist_name))

        return artist_results[0]

    @staticmethod
    def search_album(album_name):
        album_results = discogs.controller.search(album_name, type='release')

        if len(album_results) > 1:
            warnings.warn(message="The Discogs search for album '{}' returned multiple albums: {}"
                          .format(album_name, ", ".join([a.name for a in album_name])))
        elif len(album_results) == 0:
            warnings.warn(message="The Discogs search for album '{}' returned no results.".format(album_name))

        return album_results[0]

