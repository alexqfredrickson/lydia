from eyed3 import id3
import os
import re
import json


class AlbumFolder:
    def __init__(self, program, folder_name):
        self.fully_qualified_path = os.path.join(program.working_directory, folder_name)
        self.name = folder_name
        self.first_mp3 = FirstMp3(self.fully_qualified_path)

    def has_issues(self):
        return self.name_is_at_least_5_chars() is False \
               or self.name_has_uppercase_letters() \
               or self.name_starts_with_year_and_space() is False \
               or self.folder_contains_subdirectories()

    def folder_contains_subdirectories(self):
        path, dirs, files = os.walk(self.fully_qualified_path).__next__()
        return len(dirs) > 0

    def name_is_at_least_5_chars(self):
        return len(self.name) > 5

    def name_has_uppercase_letters(self):
        return any(x.isupper() for x in self.name)

    def name_starts_with_year_and_space(self):
        if self.name[0].isdigit() \
               and self.name[1].isdigit() \
               and self.name[2].isdigit() \
               and self.name[3].isdigit() \
               and self.name[4].isspace() \
               and self.name[5] == "-":

            first_two_chars = self.name[0] + self.name[1]
            return first_two_chars in ("19", "20")

        else:
            return False

    def guess_album_year(self):
        if str.isdigit(self.name[0]) is False and re.match('^.[\d]{4}', self.name):
            return self.name[1:5]

        elif re.match('^[\d]{4}', self.name):
            return self.name[0:4]


class FirstMp3:
    def __init__(self, folder_fully_qualified_path):
        self.name = os.listdir(folder_fully_qualified_path)[0]
        self.fully_qualified_path = folder_fully_qualified_path + "\\" + self.name
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

        print("Would you like to change '{}' to '{}' in '{}'?".format(old_folder_name, new_folder_name, parent_dir_name))
        user_input = input().lower()

        if user_input in ("y", "yes"):
            print("Okay, will do!")

            os.rename(
                os.path.join(parent_dir_name, old_folder_name),
                os.path.join(parent_dir_name, new_folder_name)
            )

            # TODO: when files are renamed, change the folder references to the old fq name
            # TODO: pass AlbumFolder reference such that when the album folder is renamed, the rest of the validation scripts also work as-intended
            print("Succesfully renamed '{}' to '{}'.".format(old_folder_name, new_folder_name))
