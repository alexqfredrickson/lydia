import re
import os
import json
import shutil
import discogs_client
from enum import Enum
from eyed3 import id3


class Directory:
    """
    Represents a file system directory.  Base class for lots of Lydia archive classes.
    """

    def __init__(self, path):
        """
        :param path: The path to this directory.
        """

        self.path = path
        self.dirname = os.path.dirname(path)
        self.basename = os.path.basename(self.path)

        self.all_nested_files = []

        for root, directories, files in os.walk(self.path):
            for filename in files:
                filepath = os.path.join(root, filename)
                self.all_nested_files.append(filepath)


class Mp3:
    def __init__(self, path):
        """
        :param path: The path to this .mp3 file.
        """

        self.path = path
        self.basename = os.path.basename(self.path)

        self.id_tag = id3.Tag()
        self.id_tag.parse(self.path)


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

        self.mp3s = self.get_mp3s(self.path)

        self.validator = AlbumDirectoryValidator(self)

    @staticmethod
    def get_mp3s(path):
        mp3s = []

        path, dirs, files = os.walk(path).__next__()

        for file in files:
            if file.lower().endswith(".mp3"):
                mp3s.append(Mp3(os.path.join(path, file)))

        return mp3s

    @property
    def assumed_year(self):
        standard_year_regex = "^\d{4}\s-\s"
        year_in_parentheses_with_hyphen_regex = "^\(\d{4}\)\s-\s"
        year_in_brackets_with_hyphen_regex = "^\[\d{4}\]\s-\s"
        has_something_that_looks_remotely_like_a_year_regex = r"(17\d{2}|18\d{2}|19\d{2}|20\d{2})"

        if re.match(standard_year_regex, self.basename):
            return self.basename[:4]
        if re.match(year_in_parentheses_with_hyphen_regex, self.basename) or re.match(year_in_brackets_with_hyphen_regex, self.basename):
            return self.basename[1:5]
        elif len(self.mp3s) > 0 and self.mp3s[0].id_tag.recording_date:
            return str(self.mp3s[0].id_tag.recording_date)
        elif re.match(has_something_that_looks_remotely_like_a_year_regex, self.basename):
            return re.findall(has_something_that_looks_remotely_like_a_year_regex, self.basename)[0]

        return None

    @property
    def assumed_title(self):
        has_hyphen_regex = re.compile(r"\s-\s(.*)")
        has_hyphen_regex_match = has_hyphen_regex.search(self.basename)

        if has_hyphen_regex_match:
            return has_hyphen_regex_match.group(1).lower()
        elif len(self.mp3s) > 0 and str(self.mp3s[0].id_tag.recording_date):
            return str(self.mp3s[0].id_tag.album).lower()

        return None

    def rename(self, new_basename, ask_permission=True, verbose=True):

        if ask_permission:
            print("Would you like to change '{}' to '{}' in '{}'?".format(self.basename, new_basename, self.dirname))

            user_input = input().lower()

            if user_input in ("y", "yes"):

                print("Okay, will do!")
                os.rename(self.path, os.path.join(self.dirname, new_basename))

                if verbose:
                    print("Succesfully renamed '{}' to '{}'.\n".format(self.basename, new_basename))

                self.path = os.path.join(self.dirname, new_basename)
                self.basename = new_basename

                return True

            else:
                if verbose:
                    print("Okay, I won't rename this.\n")

                return False
        else:
            os.rename(self.path, os.path.join(self.dirname, new_basename))
            self.path = os.path.join(self.dirname, new_basename)
            self.basename = new_basename

            return True

    def delete(self, ask_permission=True, verbose=True):

        path = self.path

        if ask_permission:
            print("Would you like to delete '{}' ?".format(path))

            user_input = input().lower()

            if user_input in ("y", "yes"):
                print("Okay, will do!")
                shutil.rmtree(self.path)

                if verbose:
                    print("Succesfully deleted '{}'.".format(path))

                self.path = None
                self.basename = None
                return True

            else:
                if verbose:
                    print("Okay, I won't delete this.")

                return False
        else:
            shutil.rmtree(self.path)
            self.path = None
            self.basename = None


class AlbumDirectoryValidator:
    def __init__(self, album_directory):
        self.album_directory = album_directory
        self.validation_errors = []

        self.validate()

    @property
    def is_valid(self):
        return len(self.validation_errors) == 0

    def validate(self):
        if not self.validate_basename_is_lowercase:
            print("{} looks like it has uppercase letters.".format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE)

        if not self.validate_basename_has_valid_year_and_hyphen:
            print("{} isn't in format 'YYYY - '.".format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.BASENAME_YEAR_HYPHEN_INVALID)

        if not self.validate_has_no_subdirectories:
            print("{} has subdirectories, which is kind of weird."
                  .format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.HAS_SUBDIRECTORIES)

        if not self.validate_is_not_empty:
            print("({} is empty.".format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.IS_EMPTY)

        if not self.validate_has_mp3s_or_flacs:
            print("{} doesn't contain any .mp3 or .flac files."
                  .format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.NO_MP3S_OR_FLACS)

        if not self.validate_has_year_and_title:
            print("{} doesn't have an obvious year/title."
                  .format(self.album_directory.basename))
            self.validation_errors.append(AlbumDirectoryValidationError.NO_OBVIOUS_YEAR_AND_TITLE)

    @property
    def validate_basename_is_lowercase(self):
        # if the basename is chinese/japanese/korean, let's just say it's lowercase
        if any(re.match("[\u2E80-\u9FFF]", letter) for letter in self.album_directory.basename):
            return True

        return all(letter.islower() for letter in self.album_directory.basename if letter.isalpha())

    @property
    def validate_basename_has_valid_year_and_hyphen(self):
        return re.match(r"(17|18|19|20)\d{2}\s-\s..*", self.album_directory.basename) is not None

    @property
    def validate_has_no_subdirectories(self):
        path, dirs, files = os.walk(self.album_directory.path).__next__()
        return len(dirs) == 0

    @property
    def validate_is_not_empty(self):
        return os.listdir(self.album_directory.path) != []

    @property
    def validate_has_mp3s_or_flacs(self):
        return any(x.lower().endswith(".mp3") for x in self.album_directory.all_nested_files) or \
               any(x.lower().endswith(".flac") for x in self.album_directory.all_nested_files)

    @property
    def validate_has_year_and_title(self):
        return re.match(r"\d{4}\s-\s.*", self.album_directory.basename)

    @property
    def is_valid(self):
        return len(self.validation_errors) == 0


class AlbumDirectoryValidationError(Enum):

    BASENAME_NOT_LOWERCASE = 0,
    BASENAME_YEAR_HYPHEN_INVALID = 1,
    HAS_SUBDIRECTORIES = 2,
    IS_EMPTY = 3,
    NO_MP3S_OR_FLACS = 4,
    NO_OBVIOUS_YEAR_AND_TITLE = 5


class LydiaConfig:
    def __init__(self):
        self.executing_directory = self.get_executing_directory()
        self.config_file_path = os.path.join(self.executing_directory, "config.json")
        self.working_directory = self.get_working_directory()

    @staticmethod
    def get_executing_directory():
        return os.path.dirname(os.path.abspath(__file__))

    def get_working_directory(self):
        """
        Parses the config.json file for the working directory fully qualified path.
        :return: string
        """

        with open(self.config_file_path) as config_file:
            config = json.load(config_file)
            return config[0]["working_directory"]
