import warnings
import discogs_client
from models import LydiaConfig
import time


class DiscogsApi:
    def __init__(self, verbose=False):
        """
        Initializes a DiscogsApi object.
        """

        self.controller = discogs_client.Client(
            'lydia/0.0.1-alpha',
            user_token=LydiaConfig().discogs_user_token
        )

        self.verbose = verbose

    def get_artist(self, artist_name):
        """
        Searches the Discogs database for information about a given artist.
        :param artist_name: An artist name.
        :return: A Discogs Artist object.
        """

        if self.verbose:
            print("Searching Discogs database for {}...".format(artist_name))

        artist_results = self.controller.search(artist_name, type='artist')

        if len(artist_results) > 1:
            warnings.warn(message="The Discogs search for artist '{}' returned multiple artists: {}"
                          .format(artist_name, ", ".join([a.name for a in artist_results])))
        elif len(artist_results) == 0:
            warnings.warn(message="The Discogs search for artist '{}' returned no results."
                          .format(artist_name))

        return artist_results[0]

    def get_album(self, album_name):
        """
        Searches the Discogs database for information about a given album.
        :param album_name: An album name.
        :return: A Discogs Release object.
        """

        if self.verbose:
            print("Searching Discogs database for {}...".format(album_name))

        album_results = self.controller.search(album_name, type='release')

        if len(album_results) > 1:
            warnings.warn(message="The Discogs search for album '{}' returned multiple albums: {}"
                          .format(album_name, ", ".join([a.name for a in album_name])))
        elif len(album_results) == 0:
            warnings.warn(message="The Discogs search for album '{}' returned no results.".format(album_name))

        return album_results[0]

    def get_artist_releases(self, artist_name):
        """
        Searches the Discogs database for information about a given artist's albums.

        :param artist_name: An album name.
        :return: A list of Discogs Release objects.
        :rtype: list
        """

        if self.verbose:
            print("Searching Discogs database for {} releases...".format(artist_name))

        releases = self.get_artist(artist_name).releases
        return [r for r in releases]

    def get_artist_songs(self, artist_name):
        """
        Searches the Discogs database for a list of the artist's songs.

        :param artist_name: An artist name.
        :return: A list containing all of an artist's songs.
        :rtype: list
        """

        songs = []
        releases = self.get_artist_releases(artist_name)

        for release in releases:
            for track in release.tracklist:
                print("{} - {} added to master tracklist.".format(track.data["title"], release.data["title"]))
                songs.append(track)
                time.sleep(1)

        return songs


discogs = DiscogsApi(verbose=True)
gun_club_songs = discogs.get_artist_songs("The Gun Club")

for s in gun_club_songs:
    print(s)
