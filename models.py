import re
import os
import json
import shutil
from enum import Enum
from eyed3 import id3

id3.log.setLevel("ERROR")


class Directory:
    """
    Represents a file system directory (base class for lots of Lydia-specific directory types).
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

    def rename(self, new_basename, prompt=True, verbose=True):

        new_basename = new_basename.replace("?", "")

        if prompt:
            print(f"Would you like to change '{self.basename}' to '{new_basename}' in '{self.dirname}'?")

            user_input = input().lower()

            if user_input in ("y", "yes"):

                print("Okay, will do!")
                os.rename(self.path, os.path.join(self.dirname, new_basename))

                if verbose:
                    print(f"INFO: Succesfully renamed '{self.basename}' to '{new_basename}'.")

                self.path = os.path.join(self.dirname, new_basename)
                self.basename = new_basename

                return True

            else:
                if verbose:
                    print("Okay, I won't rename this.\n")

                return False
        else:
            try:
                os.rename(self.path, os.path.join(self.dirname, new_basename))
            except FileExistsError:
                print(f"WARNING: the '{os.path.join(self.dirname, new_basename)}' directory already exists.")
                self.delete(prompt=True)

            self.path = os.path.join(self.dirname, new_basename)
            self.basename = new_basename

            return True

    def delete(self, prompt=True, verbose=True):

        path = self.path

        if prompt:
            print(f"Would you like to delete '{path}' ?")

            user_input = input().lower()

            if user_input in ("y", "yes"):
                print("Okay, will do!")
                shutil.rmtree(self.path)

                if verbose:
                    print(f"INFO: Succesfully deleted '{path}'.")

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

    def move(self, new_path, ask_permission=False, verbose=True):

        if ask_permission:
            print(f"Would you like to move '{self.path}' to '{new_path}'?")

            user_input = input().lower()

            if user_input not in ("y", "yes"):

                if verbose:
                    print("Okay, I won't move this.")

                return False
            else:
                print("Okay, will do!")

        try:
            shutil.move(self.path, new_path)

            if verbose:
                print(f"INFO: Succesfully moved '{self.path}' to '{new_path}'.")

            self.path = new_path
            self.dirname = os.path.dirname(new_path)
            self.basename = os.path.basename(new_path)

            return True

        except Exception as e:
            print(f"ERROR: failed to move {self.path}.")
            print(e)


class Mp3:
    def __init__(self, path):
        """
        :param path: The path to this .mp3 file.
        """

        self.path = path
        self.basename = os.path.basename(self.path)

        self.id_tag = id3.Tag()
        self.id_tag.parse(self.path)


class BaseArtistsDirectory(Directory):
    """
    An artists directory contains only artist-related subdirectories.
    """

    def __init__(self, path):
        Directory.__init__(self, path)
        self.subdirectories = [ArtistDirectory(x[0] for x in os.walk(path))]


class BaseAlbumsDirectory(Directory):
    """
    An albums directory is assumed to contain only album-related subdirectories.
    """

    def __init__(self, path):
        Directory.__init__(self, path)
        self.subdirectories = [AlbumDirectory(x[0] for x in os.walk(path))]


class ArtistDirectory(Directory):
    """
    An artist directory is assumed to contain only album-related subdirectories.
    """

    def __init__(self, path, validate=True, parse_mp3s=True):
        Directory.__init__(self, path)

        self.album_directories = self.get_album_directories(validate, parse_mp3s)

        if validate:
            self.validator = ArtistDirectoryValidator(self)

    def clean(self, force=False):
        for error in self.validator.validation_errors:
            if error == ArtistDirectoryValidationError.IS_EMPTY:
                if force:
                    self.delete()
                else:
                    print(f"WARNING: would have deleted '{self.basename}'.")
                break
            else:
                if error == ArtistDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                    self.rename(self.basename.lower(), prompt=False)

                if error == ArtistDirectoryValidationError.HAS_LOOSE_FILES:
                    print(f"WARNING: '{self.path}' has loose files.")

    def get_album_directories(self, validate=True, parse_mp3s=True):
        dirs = []

        for subdir in os.listdir(self.path):
            if os.path.isdir(os.path.join(self.path, subdir)):
                dirs.append(AlbumDirectory(os.path.join(self.path, subdir), validate=validate, parse_mp3s=parse_mp3s))

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
        print(f"Validating '{self.artist_directory.path}' artist directory...", end='')

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
                    print(f"    {self.artist_directory.basename} looks like it has uppercase letters.")
                elif e == ArtistDirectoryValidationError.IS_EMPTY:
                    print(f"    {self.artist_directory.basename} is empty.")
                elif e == ArtistDirectoryValidationError.HAS_LOOSE_FILES:
                    print(f"    {self.artist_directory.basename} has loose files.")

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

    def __init__(self, path, validate=True, parse_mp3s=True):
        Directory.__init__(self, path)

        if parse_mp3s:
            self.mp3s = self.get_mp3s(self.path)

        if validate:
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
        standard_year_regex = r"^\d{4}\s-\s"
        year_in_parentheses_with_hyphen_regex = r"^\(\d{4}\)\s-\s"
        year_in_brackets_with_hyphen_regex = r"^\[\d{4}\]\s-\s"
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
            return has_hyphen_regex_match.group(1).lower().replace(":", "_")
        elif len(self.mp3s) > 0 and str(self.mp3s[0].id_tag.recording_date):
            return str(self.mp3s[0].id_tag.album).lower().replace(":", "_")

    @property
    def assumed_artist(self):
        if len(self.mp3s) > 0 and str(self.mp3s[0].id_tag.artist):

            assumed_artist_name = str(self.mp3s[0].id_tag.artist).lower().strip()

            if "," in assumed_artist_name or assumed_artist_name == "none":
                print(f"WARNING: it's a bad idea to assume the artist is literally named '{assumed_artist_name}'.")
                return None

            return assumed_artist_name

        print(f"WARNING: could not determine the artist associated with {self.basename}.")
        return None

    @property
    def basename_is_lowercase(self):
        # if the basename is chinese/japanese/korean, let's just say it's lowercase
        if any(re.match("[\u2E80-\u9FFF]", letter) for letter in self.basename):
            return True

        return all(letter.islower() for letter in self.basename if letter.isalpha())

    @property
    def basename_has_valid_year_and_hyphen(self):
        try:
            return re.match(r"(17|18|19|20)\d{2}\s-\s.+", self.basename) is not None
        except Exception as e:
            print(e)
            return True

    @property
    def basename_in_yyyy_mm_dd_format(self):
        try:
            return re.match(r"^\d{4}-\d{2}-\d{2}\s.*", self.basename) is not None
        except Exception as e:
            print(e)
            return True

    @property
    def has_no_subdirectories(self):
        path, dirs, files = os.walk(self.path).__next__()
        return len(dirs) == 0

    @property
    def is_empty(self):
        return os.listdir(self.path) == []

    @property
    def has_mp3s_or_flacs(self):
        return any(x.lower().endswith(".mp3") for x in self.all_nested_files) or \
               any(x.lower().endswith(".flac") for x in self.all_nested_files)

    @property
    def has_year_hyphen_and_title(self):
        return re.match(r"\d{4}\s-\s.+", self.basename)

    @property
    def has_double_leading_year(self):
        return self.basename[0:7] == self.basename[7:14] \
               and re.match(r"^\d{4}\s-", self.basename[0:7]) is not None \
               and re.match(r"^\d{4}\s-", self.basename[7:14]) is not None

    def clean(self, force=False):
        for error in self.validator.validation_errors:
            if error == AlbumDirectoryValidationError.IS_EMPTY:
                if force:
                    self.delete()
                else:
                    print(f"WARNING: would have deleted '{self.basename}'.")
                break
            elif error == AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                self.rename(self.basename.lower(), prompt=False)

    def migrate(self, artists_directory, verbose=True):

        if not self.assumed_artist:
            print(f"WARNING: could not migrate {self.basename} - the artist name could not be determined from the contents of this "
                  "directory.")
            return None

        artist_directory_path = os.path.join(
            artists_directory,
            self.assumed_artist.lower().replace("/", "").replace(":", "_").replace('\"', '\'')
        )

        if not os.path.isdir(artist_directory_path):
            os.mkdir(artist_directory_path)

        self.move(artist_directory_path, verbose=verbose)


class AlbumDirectoryValidationError(Enum):

    BASENAME_NOT_LOWERCASE = 0,
    IS_EMPTY = 1


class AlbumDirectoryValidator:
    def __init__(self, album_directory):
        self.album_directory = album_directory
        self.validation_errors = []
        self.validate()

    @property
    def is_valid(self):
        return len(self.validation_errors) == 0

    def validate(self):
        print(f"Validating '{self.album_directory.path}' album directory...", end='')

        if not self.validate_basename_is_lowercase:
            self.validation_errors.append(AlbumDirectoryValidationError.BASENAME_NOT_LOWERCASE)

        if not self.validate_is_not_empty:
            self.validation_errors.append(AlbumDirectoryValidationError.IS_EMPTY)

        if self.is_valid:
            print("Valid!" if self.is_valid else "Invalid!")

        for e in self.validation_errors:
            if e == ArtistDirectoryValidationError.BASENAME_NOT_LOWERCASE:
                print(f"    {self.album_directory.basename} looks like it has uppercase letters.")
            elif e == ArtistDirectoryValidationError.IS_EMPTY:
                print(f"    {self.album_directory.basename} is empty.")

    @property
    def validate_basename_is_lowercase(self):
        # if the basename is chinese/japanese/korean, let's just say it's lowercase
        if any(re.match("[\u2E80-\u9FFF]", letter) for letter in self.album_directory.basename):
            return True

        return all(letter.islower() for letter in self.album_directory.basename if letter.isalpha())

    @property
    def validate_is_not_empty(self):
        return os.listdir(self.album_directory.path) != []


class LydiaConfig:
    def __init__(self):
        self.executing_directory = os.path.dirname(os.path.abspath(__file__))
        self.config_file_path = os.path.join(self.executing_directory, "config.json")

        with open(self.config_file_path) as config_file:
            config = json.load(config_file)

            self.albums_directory = config["albums_directory"]
            self.artists_directory = config["artists_directory"]
            self.staging_directory = config["staging_directory"]
            self.inventory_path = config["inventory_path"]

            self.album_validation_behavior = {
                "rename_as_lowercase":
                    config["album_validation_behavior"]["rename_as_lowercase"],
                "rename_as_year_plus_title":
                    config["album_validation_behavior"]["rename_as_year_plus_title"],
                "remove_empty_folders":
                    config["album_validation_behavior"]["remove_empty_folders"],
                "remove_folders_with_no_mp3s_or_flacs":
                    config["album_validation_behavior"]["remove_folders_with_no_mp3s_or_flacs"]
            }
