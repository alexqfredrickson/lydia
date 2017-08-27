from eyed3 import id3
import os
import re
import json


class Folder:
    def __init__(self, rootdir, folder_name):
        self.rootdir = rootdir
        self.fully_qualified_path = rootdir + "\\" + folder_name
        self.name = folder_name
        self.first_mp3 = FirstMp3(self.fully_qualified_path)
        self.album_year = None

    def name_is_valid(self):
        return self.name_is_at_least_5_chars() \
               and self.name_has_uppercase_letters() is False \
               and self.name_starts_with_year_and_space()

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
            if first_two_chars in ("19", "20"):
                return True
        else:
            return False

    def guess_album_year(self):
        if str.isdigit(self.name[0]) is False and re.match('^.[\d]{4}', self.name):
            print("FYI - I think the album year might be {}.".format(self.name[1:5]))
            return self.name[1:5]

        elif re.match('^[\d]{4}', self.name):
            print("FYI - I think the album year might be {}.".format(self.name[0:4]))
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
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def get_working_directory(self):
        """
        Parses the config.json file for the working directory.
        :return: string
        """

        with open(self.config_file_path) as config_file:
            config = json.load(config_file)
            return config[0]["working_directory"]

    @staticmethod
    def prompt_rename(old_dir_name, new_dir_name):
        print("Would you like to change '{}' to '{}'?".format(old_dir_name, new_dir_name))
        user_input = input().lower()

        if user_input in ("y", "yes"):
            print("Okay, will do!")
            os.rename(old_dir_name, new_dir_name)
            # TODO: when files are renamed, change the folder references to the old fq name
            print("Succesfully renamed '{}' to '{}'.".format(old_dir_name, new_dir_name))

program = Program()

for folder in os.listdir(program.working_directory):
    f = Folder(program.working_directory, folder)

    if f.name_is_valid():
        print("'{}' looks legit!".format(f.name))
    else:
        if f.name_is_at_least_5_chars() is False:
            print("'{}' has way too short of a name to signify anything really.".format(folder))
            continue

        if f.name_has_uppercase_letters():
            print("No big deal but it looks like '{}' has uppercase letters.".format(f.name))

            program.prompt_rename(
                f.fully_qualified_path, os.path.join(os.path.join(program.working_directory, f.name.lower()))
            )

        if f.name_starts_with_year_and_space() is False:
            print("'{}' doesn't start with 'YYYY - '. Let's attempt to infer it from the first .mp3's ID3 tag.".format(
                f.name))

            if os.path.isdir(f.first_mp3.fully_qualified_path) is False:
                print("Examining {}.".format(f.first_mp3.fully_qualified_path))

                if f.first_mp3.file_tag.recording_date is not None and f.first_mp3.file_tag.album is not None:
                    print("The old folder name is '{}'.".format(f.fully_qualified_path))

                    program.prompt_rename(
                        f.fully_qualified_path,
                        os.path.join(os.path.join(program.working_directory, str(f.first_mp3.file_tag.recording_date)
                                                  + " - " + f.first_mp3.file_tag.album.lower()))
                    )

                else:
                    if f.first_mp3.file_tag.recording_date is None and f.first_mp3.file_tag.album is None:
                        print("Looks like the .mp3s in here don't have album recording dates, nor album names, "
                              "so I'm going to skip this folder for now.")
                    elif f.first_mp3.file_tag.recording_date is None:
                        print("Looks like this .mp3 doesn't have an album recording date.")
                        f.album_year = f.guess_album_year()
                    elif f.first_mp3.file_tag.recording_date is None:
                        print("Looks like this .mp3 doesn't have an album name.")
                    else:
                        print("Something really fucked up happened.")
    print("\n")
