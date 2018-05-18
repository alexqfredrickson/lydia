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

        self.validator = ArtistDirectoryValidator(self)
        self.album_directories = self.get_album_directories()

    def clean(self, dry_run):
        for error in self.validator.validation_errors:
            if error == ArtistDirectoryValidationError.IS_EMPTY:
                if dry_run:
                    print("DRY RUN: would have deleted '{}'.".format(self.basename))
                else:
                    self.delete()

                break
            else:
                if error == ArtistDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                    self.rename(self.basename.lower(), ask_permission=False)

                if error == ArtistDirectoryValidationError.HAS_LOOSE_FILES:
                    print("WARNING: '{}' has loose files.".format(self.path))

    def get_album_directories(self):
        dirs = []

        for subdir in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, subdir)):
                dirs.append(AlbumDirectory(os.path.join(self.path, subdir)))

        return dirs


class ArtistDirectoryValidator:
    def __init__(self, artist_directory):
        self.artist_directory = artist_directory
        self.validation_errors = []

        self.validate()

    @property
    def is_valid(self):
        return len(self.validation_errors) == 0

    def validate(self):
        print("Validating '{}' artist directory...".format(self.artist_directory.path), end='')

        if not self.validate_basename_is_lowercase:
            self.validation_errors.append(ArtistDirectoryValidationError.BASENAME_NOT_LOWERCASE)

        if not self.validate_is_not_empty:
            self.validation_errors.append(ArtistDirectoryValidationError.IS_EMPTY)

        if not self.validate_no_loose_files:
            self.validation_errors.append(ArtistDirectoryValidationError.HAS_LOOSE_FILES)

        if self.is_valid:
            print("valid!")

        else:
            print("INVALID!")

            for e in self.validation_errors:
                if e == ArtistDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                    print("    {} looks like it has uppercase letters.".format(self.artist_directory.basename))
                elif e == ArtistDirectoryValidationError.IS_EMPTY:
                    print("    {} is empty.".format(self.artist_directory.basename))
                elif e == ArtistDirectoryValidationError.HAS_LOOSE_FILES:
                    print("    {} has loose files.".format(self.artist_directory.basename))

    @property
    def validate_basename_is_lowercase(self):
        # if the basename is chinese/japanese/korean, let's just say it's lowercase
        if any(re.match("[\u2E80-\u9FFF]", letter) for letter in self.artist_directory.basename):
            return True

        return all(letter.islower() for letter in self.artist_directory.basename if letter.isalpha())

    @property
    def validate_no_loose_files(self):
        contents = [os.path.join(self.artist_directory.path, c) for c in os.listdir(self.artist_directory.path)]
        return any(os.path.isfile(c) for c in contents) is False

    @property
    def validate_is_not_empty(self):
        return os.listdir(self.artist_directory.path) != []


class ArtistDirectoryValidationError(Enum):

    BASENAME_NOT_LOWERCASE = 0,
    IS_EMPTY = 1,
    HAS_LOOSE_FILES = 2


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
        if re.match(year_in_parentheses_with_hyphen_regex, self.basename) \
                or re.match(year_in_brackets_with_hyphen_regex, self.basename):
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

    def clean(self):
        for error in self.validator.validation_errors:

            if error in [AlbumDirectoryValidationError.IS_EMPTY,
                         AlbumDirectoryValidationError.NO_MP3S_OR_FLACS]:
                self.delete()
                break
            else:
                if error == AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                    self.rename(self.basename.lower(), ask_permission=False)

                if error == AlbumDirectoryValidationError.NO_OBVIOUS_YEAR_AND_TITLE:

                    if self.assumed_year is not None and self.assumed_title is not None:
                        old_name = self.basename
                        new_name = "{} - {}".format(self.assumed_year, self.assumed_title).replace("\"", "")

                        if "/" in new_name:
                            print("WARNING: couldn't clean up '{}' (the new name would have a forward slash in it)."
                                  .format(self.path))
                            break

                        if old_name != new_name:
                            self.rename(new_name)
                    else:
                        print("WARNING: couldn't clean up '{}'.".format(self.path))


class AlbumDirectoryValidator:
    def __init__(self, album_directory):
        self.album_directory = album_directory
        self.validation_errors = []

        self.validate()

    @property
    def is_valid(self):
        return len(self.validation_errors) == 0

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
    def validate_has_year_hyphen_and_title(self):
        return re.match(r"\d{4}\s-\s.+", self.album_directory.basename)

    def validate(self):

        print("Validating '{}' album directory...".format(self.album_directory.path), end='')

        if not self.validate_basename_is_lowercase:
            self.validation_errors.append(AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE)

        if not self.validate_has_no_subdirectories:
            self.validation_errors.append(AlbumDirectoryValidationError.HAS_SUBDIRECTORIES)

        if not self.validate_is_not_empty:
            self.validation_errors.append(AlbumDirectoryValidationError.IS_EMPTY)

        if not self.validate_has_mp3s_or_flacs:
            self.validation_errors.append(AlbumDirectoryValidationError.NO_MP3S_OR_FLACS)

        if not self.validate_has_year_hyphen_and_title:
            self.validation_errors.append(AlbumDirectoryValidationError.NO_OBVIOUS_YEAR_AND_TITLE)

        if self.is_valid:
            print("valid!")

        else:
            print("INVALID!")

            for e in self.validation_errors:
                if e == AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                    print("    {} looks like it has uppercase letters.".format(self.album_directory.basename))
                elif e == AlbumDirectoryValidationError.HAS_SUBDIRECTORIES:
                    print("    {} has subdirectories, which is kind of weird.".format(self.album_directory.basename))
                elif e == AlbumDirectoryValidationError.IS_EMPTY:
                    print("    {} is empty.".format(self.album_directory.basename))
                elif e == AlbumDirectoryValidationError.NO_MP3S_OR_FLACS:
                    print("    {} doesn't contain any .mp3 or .flac files.".format(self.album_directory.basename))
                elif  e == AlbumDirectoryValidationError.NO_OBVIOUS_YEAR_AND_TITLE:
                    print("    {} doesn't have an obvious year/title.".format(self.album_directory.basename))


class AlbumDirectoryValidationError(Enum):

    BASENAME_NOT_LOWERCASE = 0,
    HAS_SUBDIRECTORIES = 2,
    IS_EMPTY = 3,
    NO_MP3S_OR_FLACS = 4,
    NO_OBVIOUS_YEAR_AND_TITLE = 5


class LydiaConfig:
    def __init__(self):
        self.executing_directory = self.get_executing_directory()
        self.config_file_path = os.path.join(self.executing_directory, "config.json")
        self.working_directory = self.get_config_value("working_directory")
        self.archive_directory = self.get_config_value("archive_directory")

    @staticmethod
    def get_executing_directory():
        return os.path.dirname(os.path.abspath(__file__))

    def get_config_value(self, name):
        """
        Parses the config.json file for some value.
        :return: string
        """

        with open(self.config_file_path) as config_file:
            config = json.load(config_file)
            return config[0][name]
