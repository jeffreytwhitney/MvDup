import shutil
import os
import time

from lib.Utilities import (get_stored_ini_value, get_unencoded_file_lines,
                           write_lines_to_file, get_index_containing_text)


def replace_text_with_prompt(file_lines: list[str], input_filepath: str):

    for line in file_lines:
        line.replace("Text EMPLOYEE: Text", "Prompt EMPLOYEE: Input")
        line.replace("Text JOB: Text", "Prompt JOB: Input")
        line.replace("Text MACHINE: Text", "Prompt MACHINE: Input")
        line.replace("Text SEQUENCE: Text", "Prompt SEQUENCE: Input")
    write_lines_to_file(input_filepath, file_lines)


def convert_export_to_spc_style(file_lines: list[str], input_filepath: str):

    idx = get_index_containing_text(file_lines, "Text REV LETTER:")
    file_lines.pop(idx)

    idx = get_index_containing_text(file_lines, "Text OPERATION:")
    file_lines.pop(idx)

    idx = get_index_containing_text(file_lines, "Prompt SEQUENCE:")
    file_lines.pop(idx)

    idx = get_index_containing_text(file_lines, "Text PT")
    line = file_lines[idx]
    file_lines[idx] = line.split(",")[1]

    idx = get_index_containing_text(file_lines, "Prompt EMPLOYEE")
    line = file_lines[idx]
    file_lines[idx] = line.split(",")[1]

    idx = get_index_containing_text(file_lines, "Prompt JOB")
    line = file_lines[idx]
    file_lines[idx] = line.split(",")[1]

    idx = get_index_containing_text(file_lines, "Prompt MACHINE")
    line = file_lines[idx]
    file_lines[idx] = line.split(",")[1]

    idx = get_index_containing_text(file_lines, "Text IN PROCESS")
    line = file_lines[idx]
    file_lines[idx] = line.split(",")[1]

    write_lines_to_file(input_filepath, file_lines)


def main():
    input_directory = get_stored_ini_value("Paths", "input_path", "settings")
    primary_output_directory = get_stored_ini_value("Paths", "primary_output_path", "settings")
    secondary_output_directory = get_stored_ini_value("Paths", "output_path_two", "settings")
    convert_to_prompts = bool(get_stored_ini_value("ProcessSwitches", "convert_text_to_prompt", "settings"))
    duplicate_file = bool(get_stored_ini_value("ProcessSwitches", "duplicate_file", "settings"))
    while True:
        for filename in os.listdir(input_directory):
            change_to_filename = get_stored_ini_value("ProcessSwitches", "change_to_filename", "settings")
            input_filepath = os.path.join(input_directory, filename)
            file_lines = get_unencoded_file_lines(input_filepath)
            primary_output_filepath = os.path.join(primary_output_directory, filename)
            secondary_output_filepath = os.path.join(secondary_output_directory, change_to_filename)
            if convert_to_prompts:
                replace_text_with_prompt(file_lines, input_filepath)
            if duplicate_file:
                shutil.copyfile(input_filepath, primary_output_filepath)
                convert_export_to_spc_style(file_lines, input_filepath)
                shutil.move(input_filepath, str(secondary_output_filepath))
            else:
                shutil.move(input_filepath, str(primary_output_filepath))
        time.sleep(6)


if __name__ == "__main__":
    main()
