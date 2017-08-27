import os
import lydia.models

program = models.Program()

working_directory_file_names = os.listdir(program.working_directory)

for file_name in working_directory_file_names:

    current_file_path = os.path.join(program.working_directory, file_name)

    if os.path.isdir(current_file_path) is False:
        print("It looks like '{}' is a file, not a folder.".format(file_name))
        continue

    album_folder = models.AlbumFolder(program, file_name)

    if album_folder.has_issues() is False:
        print("'{}' looks legit!".format(album_folder.name))
        print("")
        continue
    else:

        if album_folder.name_is_at_least_5_chars() is False:
            print("'{}' has a bewilderingly short name and I'm just going to stop here.".format(file_name))
            print("")
            continue

        if album_folder.name_has_uppercase_letters():
            program.prompt_folder_rename(
                album_folder.name,
                album_folder.name.lower(),
                program.working_directory,
                "No big deal but it looks like '{}' has uppercase letters.".format(album_folder.name)
            )

        if album_folder.folder_contains_subdirectories():
            print("This folder has subdirectories, which is kind of weird, so I'm skipping this one.")
            print("")
            continue

        if album_folder.name_starts_with_year_and_space() is False:
            print("'{}' doesn't start with 'YYYY - '.".format(album_folder.name))

            print("Let's try to infer the proper folder name from '{}'s ID3 tag."
                  .format(album_folder.first_mp3.fully_qualified_path))

            if album_folder.first_mp3.file_tag.recording_date and album_folder.first_mp3.file_tag.album:

                program.prompt_folder_rename(
                    album_folder.name,
                    "{} - {}".format(
                        str(album_folder.first_mp3.file_tag.recording_date),
                        album_folder.first_mp3.file_tag.album.lower()
                    ),
                    program.working_directory,
                    "I think I figured this out."
                )

            elif album_folder.first_mp3.file_tag.recording_date is None \
                    and album_folder.first_mp3.file_tag.album is None:
                print("Never mind! The .mp3s in here don't have album recording dates nor album names. "
                      "I'm going to skip this one.")
                print("")
                continue

            elif album_folder.first_mp3.file_tag.recording_date is None:

                if album_folder.guess_album_year():
                    program.prompt_folder_rename(
                        album_folder.name,
                        "{} - {}".format(
                            album_folder.guess_album_year(),
                            album_folder.first_mp3.file_tag.album.lower()
                        ),
                        program.working_directory,
                        "I think the album name is '{}' but I'm still lost on the album year. I think it might be {}."
                            .format(album_folder.first_mp3.file_tag.album, album_folder.guess_album_year())
                    )
                else:
                    print("Ahhhh nope, couldn't figure out the album year.")
                    print("")
                    continue

            else:
                print("Pretty much everything about this album folder name is fucked up, so I'm moving on.")
                print("")
                continue
