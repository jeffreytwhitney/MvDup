import shutil
import os
import time

from lib.Utilities import get_stored_ini_value, get_unencoded_file_lines, write_lines_to_file


def process_export(input_filepath: str):
    file_lines = get_unencoded_file_lines(input_filepath)
    for line in file_lines:
        line.replace("Text EMPLOYEE: Text", "Prompt EMPLOYEE: Input")
        line.replace("Text JOB: Text", "Prompt JOB: Input")
        line.replace("Text MACHINE: Text", "Prompt MACHINE: Input")
        line.replace("Text SEQUENCE: Text", "Prompt SEQUENCE: Input")
    write_lines_to_file(input_filepath, file_lines)


def main():
    input_directory = get_stored_ini_value("Paths", "input_path", "settings")
    output_one = get_stored_ini_value("Paths", "output_path_one", "settings")
    output_two = get_stored_ini_value("Paths", "output_path_two", "settings")
    convert_to_prompts = bool(get_stored_ini_value("ProcessSwitches", "convert_texts_to_prompts", "settings"))

    while True:
        for filename in os.listdir(input_directory):
            change_to_filename = get_stored_ini_value("ProcessSwitches", "change_to_filename", "settings")
            input_filepath = os.path.join(input_directory, filename)
            output_one_filepath = os.path.join(output_one, filename)
            output_two_filepath = os.path.join(output_two, change_to_filename)
            if convert_to_prompts:
                process_export(input_filepath)
            shutil.copyfile(input_filepath, output_one_filepath)
            shutil.move(input_filepath, str(output_two_filepath))
        time.sleep(6)


if __name__ == "__main__":
    main()
