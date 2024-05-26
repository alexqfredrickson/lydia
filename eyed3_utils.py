import os
import eyed3


class Eyed3Utils:
    """
    Miscellaneous eyed3 utilities.

    """
    def __init__(self):
        pass

    @staticmethod
    def fix_idv3_metadata(artist_directory=None, album_directory=None, artist=None, album=None):
        """
        Manually curates IDv3 metadata - for instance: for albums missing artist information.
        """

        if not artist_directory and not album_directory:
            print("ERROR: please specify an artist or album directory.")
            return None
        elif artist_directory and album_directory:
            print("ERROR: please specify only one artist or album directory.")
            return None

        if album_directory:
            for file in os.listdir(album_directory):
                if file.lower().endswith(".mp3"):
                    mp3_file = file
                    metadata = eyed3.load(os.path.join(album_directory, mp3_file))

                    if not metadata.tag:
                        metadata.initTag()

                    if artist:
                        if metadata.tag.artist != artist or metadata.tag.album_artist != artist:
                            metadata.tag.artist = artist
                            metadata.tag.album_artist = artist

                            try:
                                metadata.tag.save()
                                print(
                                    f"INFO: {os.path.join(album_directory, mp3_file)} updated to"
                                    f" reflect that {artist} is the artist and album_artist."
                                )
                            except NotImplementedError:
                                pass

                            metadata = eyed3.load(os.path.join(album_directory, mp3_file))
                            print(metadata.tag.artist)

        elif artist_directory:  # todo: lazy alert; please fix

            for ad in os.listdir(artist_directory):
                for file in os.listdir(os.path.join(artist_directory, ad)):
                    if file.lower().endswith(".mp3"):
                        mp3_file = file
                        metadata = eyed3.load(os.path.join(artist_directory, ad, mp3_file))

                        if not metadata.tag:
                            metadata.initTag()

                        if artist:

                            if metadata.tag.artist != artist or metadata.tag.album_artist != artist:
                                metadata.tag.artist = artist
                                metadata.tag.album_artist = artist

                                try:
                                    metadata.tag.save()
                                    print(
                                        f"INFO: {os.path.join(artist_directory, ad, mp3_file)} updated to"
                                        f" reflect that {artist} is the artist and album_artist."
                                    )
                                except NotImplementedError:
                                    pass

                                metadata = eyed3.load(os.path.join(artist_directory, ad, mp3_file))
                                print(metadata.tag.artist)