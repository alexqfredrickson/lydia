import re
import os
import json
from eyed3 import id3


class Directory:

    def __init__(self, path):
        self.path = path
        self.basename = os.path.basename(self.path)


class SortedArchive(Directory):
    """
    A sorted archive contains only artist-related subdirectories.
    """

    def __init__(self, path):
        Directory.__init__(self, path)
        self.subdirectories = [ArtistDirectory(x[0] for x in os.walk(path))]


class UnsortedArchive(Directory):
    """
    An unsorted archive is assumed to contain only album-related subdirectories.
    """

    def __init__(self, path):
        Directory.__init__(self, path)
        self.subdirectories = [AlbumDirectory(x[0] for x in os.walk(path))]


class ArtistDirectory(Directory):
    """
    An artist directory is assumed to contain only album-related subdirectories.
    """

    def __init__(self, path):
        Directory.__init__(self, path)
        self.subdirectories = [AlbumDirectory(x[0] for x in os.walk(path))]


class AlbumDirectory(Directory):
    """
    An album directory is assumed to contain only .mp3 files.
    """

    def __init__(self, path):
        Directory.__init__(self, path)

        self.suggested_name = None

        for working_dir_path, album_dirs, mp3_file_names in os.walk(self.path):
            self.first_mp3 = Mp3(os.path.join(working_dir_path, mp3_file_names[0]))

    @property
    def album_name_is_at_least_5_chars(self):
        return len(self.basename) > 5

    @property
    def album_name_is_lowercase(self):
        return all(letter.islower() for letter in self.basename)

    @property
    def album_name_has_valid_year_and_title(self):
        return re.match(self.basename, r"^(17|18|19|20)\d{2}\s-\s..*")

    @property
    def contains_subdirectories(self):
        path, dirs, files = os.walk(self.basename).__next__()
        return len(dirs) > 0

    @property
    def album_directory_is_valid(self):
        return self.album_name_is_at_least_5_chars \
               and self.album_name_is_lowercase \
               and self.album_name_has_year_and_title \
               and self.contains_subdirectories is False

    def guess_album_year(self):
        valid_year_regex = r"(17|18|19|20)\d{2}"
        return re.search(valid_year_regex, self.basename)


class Mp3:

    def __init__(self, path):
        self.path = path
        self.basename = os.path.basename(self.path)
        self.id_tag = id3.Tag().parse(self.path)


class Program:
    def __init__(self):
        self.executing_directory = self.get_executing_directory()
        self.config_file_path = os.path.join(self.executing_directory, "config.json")
        self.working_directory = self.get_working_directory()

    @staticmethod
    def get_executing_directory():
        return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    def get_working_directory(self):
        """
        Parses the config.json file for the working directory fully qualified path.
        :return: string
        """

        with open(self.config_file_path) as config_file:
            config = json.load(config_file)
            return config[0]["working_directory"]

    @staticmethod
    def prompt_folder_rename(old_folder_name, new_folder_name, parent_dir_name, message=None):
        if message:
            print(message)

        print("Would you like to change '{}' to '{}' in '{}'?"
              .format(old_folder_name, new_folder_name, parent_dir_name))

        user_input = input().lower()

        if user_input in ("y", "yes"):
            print("Okay, will do!")

            os.rename(
                os.path.join(parent_dir_name, old_folder_name),
                os.path.join(parent_dir_name, new_folder_name)
            )

            print("Succesfully renamed '{}' to '{}'.".format(old_folder_name, new_folder_name))
            return True

        else:
            return False
