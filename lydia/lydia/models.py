import re
import os
import json
from eyed3 import id3


class AlbumValidator:
    def __init__(self, name, path):
        self.name = name
        self.suggested_name = None
        self.path = path

        for working_dir_path, album_dirs, mp3_file_names in os.walk(self.path):
            self.first_mp3 = FirstMp3(os.path.join(working_dir_path, mp3_file_names[0]))

    def name_is_problematic(self):
        return not self.name_is_at_least_5_chars() \
               or self.name_has_uppercase_letters() \
               or not self.name_starts_with_year_and_space()

    def path_is_problematic(self):
        return self.folder_contains_subdirectories()

    def name_is_at_least_5_chars(self):
        return len(self.name) > 5

    def name_has_uppercase_letters(self):
        return any(x.isupper() for x in self.name)

    def name_starts_with_year_and_space(self):
        if not self.name_is_at_least_5_chars():
            return False

        if self.name[0].isdigit() \
                and self.name[1].isdigit() \
                and self.name[2].isdigit() \
                and self.name[3].isdigit() \
                and self.name[4].isspace() \
                and self.name[5] == "-":

            first_two_chars = self.name[0] + self.name[1]
            return first_two_chars in ("19", "20")

        return False

    def folder_contains_subdirectories(self):
        path, dirs, files = os.walk(self.path).__next__()
        return len(dirs) > 0

    def guess_album_year(self):
        if not str.isdigit(self.name[0]) and re.match('^.[\d]{4}', self.name):
            return self.name[1:5]

        elif re.match('^[\d]{4}', self.name):
            return self.name[0:4]


class FirstMp3:
    def __init__(self, mp3_path):
        self.name = os.path.basename(mp3_path)
        self.fully_qualified_path = mp3_path
        self.file_tag = id3.Tag()
        self.file_tag.parse(self.fully_qualified_path)


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
