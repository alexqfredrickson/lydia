from .models import *


def init():
    program = Program()

    for working_dir_path, album_dirs, mp3_file_names in os.walk(program.working_directory):

        for album_name in album_dirs:

            album_validator = AlbumValidator(album_name, os.path.join(working_dir_path, album_name))

            if album_validator.path_is_problematic() is False and album_validator.name_is_problematic() is False:
                print("'{}' looks legit!".format(album_name))
                print("")
                continue
            else:
                if album_validator.name_has_uppercase_letters() is True:

                    album_validator.suggested_name = album_validator.name.lower()

                    if program.prompt_folder_rename(
                            album_validator.name,
                            album_validator.suggested_name,
                            working_dir_path,
                            "No big deal but it looks like '{}' has uppercase letters.".format(album_validator.name)
                    ) is True:

                        album_name = album_validator.suggested_name
                        album_validator = AlbumValidator(album_name, os.path.join(working_dir_path, album_name))

                # TODO: dont stop - guess the album name and year
                # if album_validator.name_is_at_least_5_chars() is False:
                #     print("'{}' has a bewilderingly short name and I'm just going to stop here.".format(album_name))
                #     print("")
                #     continue

                if album_validator.folder_contains_subdirectories():
                    print("This folder has subdirectories, which is kind of weird, so I'm skipping this one.")
                    print("")
                    continue

                if album_validator.name_starts_with_year_and_space() is False:
                    print("'{}' doesn't start with 'YYYY - '.".format(album_validator.name))

                    print("Let's try to infer the proper folder name from '{}'s ID3 tag."
                          .format(album_validator.first_mp3.fully_qualified_path))

                    if album_validator.first_mp3.file_tag.recording_date and album_validator.first_mp3.file_tag.album:

                        album_validator.suggested_name = "{} - {}".format(
                                str(album_validator.first_mp3.file_tag.recording_date),
                                album_validator.first_mp3.file_tag.album.lower()
                            )

                        if program.prompt_folder_rename(
                                album_validator.name,
                                album_validator.suggested_name,
                                working_dir_path,
                                "I think I figured this out."
                        ) is True:
                            album_name = album_validator.suggested_name
                            album_validator = AlbumValidator(album_name, os.path.join(working_dir_path, album_name))

                    elif album_validator.first_mp3.file_tag.recording_date is None \
                            and album_validator.first_mp3.file_tag.album is None:
                        print("Never mind! The .mp3s in here don't have album recording dates nor album names. "
                              "I'm going to skip this one.")
                        print("")
                        continue

                    elif album_validator.first_mp3.file_tag.recording_date is None:

                        if album_validator.guess_album_year() is not None:

                            album_validator.suggested_name = "{} - {}".format(
                                        album_validator.guess_album_year(),
                                        album_validator.first_mp3.file_tag.album.lower()
                                    )

                            if program.prompt_folder_rename(
                                    album_validator.name,
                                    album_validator.suggested_name,
                                    working_dir_path,
                                    "I think the album name is '{}' but I'm still lost on the album year. "
                                    "I think it might be {}.".format(
                                        album_validator.first_mp3.file_tag.album, album_validator.guess_album_year())
                            ) is True:
                                album_name = album_validator.suggested_name
                                album_validator = AlbumValidator(album_name, os.path.join(working_dir_path, album_name))
                        else:
                            print("Ahhhh nope, couldn't figure out the album year.")
                            print("")
                            continue

                    else:
                        print("Pretty much everything about this album folder name is fucked up, so I'm moving on.")
                        print("")
                        continue

