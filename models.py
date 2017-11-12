import re
import os
import shutil
import json
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

        self.mp3s = []

        path, dirs, files = os.walk(self.path).__next__()

        for file in files:
            if file.lower().endswith(".mp3"):
                self.mp3s.append(Mp3(os.path.join(path, file)))

    @property
    def basename_is_lowercase(self):
        # if the basename is chinese/japanese/korean, let's just say it's lowercase
        if any(re.match("[\u2E80-\u9FFF]", letter) for letter in self.basename):
            return True

        return all(letter.islower() for letter in self.basename if letter.isalpha())

    @property
    def basename_has_valid_year_and_title(self):
        return re.match(r"(17|18|19|20)\d{2}\s-\s..*", self.basename) is not None

    @property
    def basename_is_valid(self):
        return self.basename_is_lowercase and self.basename_has_valid_year_and_title

    @property
    def contains_subdirectories(self):
        path, dirs, files = os.walk(self.path).__next__()
        return len(dirs) > 0

    @property
    def is_empty(self):
        return os.listdir(self.path) == []

    @property
    def has_mp3s(self):
        return any(x.lower().endswith(".mp3") for x in self.all_nested_files)

    @property
    def has_flacs(self):
        return any(x.lower().endswith(".flac") for x in self.all_nested_files)

    @property
    def contents_are_valid(self):
        return self.contains_subdirectories is False and self.is_empty is False and self.has_mp3s

    @property
    def is_valid(self):
        return self.basename_is_valid and self.contents_are_valid

    def guess_album_year(self):
        valid_year_regex = r"(17\d{2}|18\d{2}|19\d{2}|20\d{2})"
        return re.findall(valid_year_regex, self.basename)

    def rename(self, new_basename, contextual_message=None, ask_permission=True, verbose=True):

        if contextual_message:
            print(contextual_message)

        if ask_permission:
            print("Would you like to change '{}' to '{}' in '{}'?".format(self.basename, new_basename, self.dirname))

            user_input = input().lower()

            if user_input in ("y", "yes"):
                print("Okay, will do!")
                os.rename(self.path, os.path.join(self.dirname, new_basename))

                if verbose:
                    print("Succesfully renamed '{}' to '{}'.".format(self.basename, new_basename))

                self.path = os.path.join(self.dirname, new_basename)
                self.basename = new_basename

                return True

            else:
                if verbose:
                    print("Okay, I won't rename this.")

                return False
        else:
            os.rename(self.path, os.path.join(self.dirname, new_basename))
            self.path = os.path.join(self.dirname, new_basename)
            self.basename = new_basename

            return True

    def delete(self, contextual_message=None, ask_permission=True, verbose=True):

        path = self.path

        if contextual_message:
            print(contextual_message)

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

    def lint_basename(self):
        if self.basename_is_lowercase is False:
            self.rename(
                self.basename.lower(),
                contextual_message="No big deal but it looks like '{}' has uppercase letters.".format(self.basename)
            )

        if self.basename_has_valid_year_and_title is False:
            print("'{}' isn't in format 'YYYY - '.".format(self.basename))

            album_renamed = False

            if re.match(r"^\(\d{4}\)\s", self.basename) or re.match(r"^\[\d{4}\]\s", self.basename):
                album_renamed = self.rename(
                    "{0} - {1}" .format(self.basename[1:5], self.basename[7:]),
                    contextual_message="It looks like the album year is specified, just in a weird format."
                )

            if not album_renamed:

                print("Attempting to infer the album name from the first .mp3's ID3 tag...")

                inferred_album_year, inferred_album_name = None, None

                if self.has_mp3s:
                    inferred_album_year = self.mp3s[0].id_tag.recording_date
                    inferred_album_name = self.mp3s[0].id_tag.album

                if inferred_album_year and inferred_album_name:
                    self.rename(
                        "{} - {}" .format(str(inferred_album_year), inferred_album_name.lower())
                    )
                elif self.guess_album_year() and inferred_album_name:
                    self.rename(
                        "{} - {}" .format(self.guess_album_year()[0], inferred_album_name.lower())
                    )
                elif self.guess_album_year():
                    self.rename(
                        "{0} - {1}" .format(self.guess_album_year()[0], self.basename),
                        contextual_message="Okay, last try."
                    )
                else:
                    print("... I couldn't figure out what to rename this to.\n")

    def lint_contents(self):
        if self.contains_subdirectories:
            print("{0} has subdirectories, which is kind of weird... FYI.".format(self.basename))

        if self.is_empty:
            self.delete(contextual_message="{0} folder doesn't have any files.".format(self.basename))

        if self.has_mp3s is False and self.has_flacs is False:
            self.delete(contextual_message="{0} folder doesn't have any .mp3 or .flac files.".format(self.basename))


class Program:
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

