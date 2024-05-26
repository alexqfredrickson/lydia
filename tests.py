import unittest
from eyed3_utils import Eyed3Utils


class LydiaTests(unittest.TestCase):

    eyed3_utils = Eyed3Utils()

    def test_fix_idv3_metadata(self):
        artist_directory = ""
        album_directory = ""
        artist_name = ""
        album_name = ""

        self.eyed3_utils.fix_idv3_metadata(
            artist_directory=artist_directory, album_directory=album_directory, artist=artist_name, album=album_name
        )

        self.assertTrue(True)

