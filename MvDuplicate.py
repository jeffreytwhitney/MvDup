import configparser
import os
import shutil
import sys
import time
from datetime import datetime
from typing import List


def write_error(e: Exception):
    current_datetime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    complete_error_message = f"{current_datetime}: {e}"
    error_path = os.path.join(resolve_path(), "error_log.txt")
    with open(error_path, "a") as f:
        f.write(f"{complete_error_message}\n")


def write_error_message(error_message: str):
    current_datetime = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
    complete_error_message = f"{current_datetime}: {error_message}"
    error_path = os.path.join(resolve_path(), "error_log.txt")
    with open(error_path, "a") as f:
        f.write(f"{complete_error_message}\n")


def get_index_containing_text(file_lines: list[str], text_to_find: str) -> int:
    return next(
        (i for i, l in enumerate(file_lines)
         if l.upper().find(text_to_find.upper()) != -1), -1
    )


def resolve_path():
    return (
        os.path.abspath(os.path.dirname(sys.executable))
        if getattr(sys, "frozen", False)
        else os.path.abspath(os.path.join(os.getcwd()))
    )


def get_ini_file_path(ini_file_name):
    try:
        current_dir = resolve_path()
        return current_dir + "\\" + ini_file_name + ".ini"

    except:
        return ""


def get_stored_ini_value(ini_section, ini_key, ini_filename):
    config_value = ""
    ini_file_path = get_ini_file_path(ini_filename)
    config = configparser.ConfigParser()
    config.read(ini_file_path)
    try:
        config_value = config.get(ini_section, ini_key)
    except:
        config_value = ""
    return config_value


def get_unencoded_file_lines(file_path: str) -> list[str]:
    try:
        with open(file_path, "r") as f:
            return f.readlines()
    except Exception as e:
        write_error(e)
        return []


def write_lines_to_file(output_filepath: str, file_lines: list[str], newline='\n'):
    try:
        with open(output_filepath, 'w+', newline=f'{newline}') as f:
            for line in file_lines:
                f.write(f"{line}")
    except Exception as e:
        write_error(e)


def check_file_paths() -> bool:
    try:
        ini_filepath = get_ini_file_path("settings")
        input_path = get_stored_ini_value("Paths", "input_path", "settings")
        primary_output_path = get_stored_ini_value("Paths", "primary_output_path", "settings")
        secondary_output_path = get_stored_ini_value("Paths", "secondary_output_path", "settings")

        if not ini_filepath:
            write_error_message("No ini file path")
            return False
        if not os.path.exists(ini_filepath):
            write_error_message(f"Ini file path '{ini_filepath}' does not exist.")
            return False

        if not input_path:
            write_error_message("No input path")
            return False
        if not os.path.exists(input_path):
            write_error_message(f"Input path '{input_path}' does not exist")
            return False

        if not primary_output_path:
            write_error_message("No primary output path")
            return False
        if not os.path.exists(primary_output_path):
            write_error_message(f"Primary output path '{primary_output_path}' does not exist")
            return False

        if not secondary_output_path:
            write_error_message("No secondary output path")
            return False
        if not os.path.exists(secondary_output_path):
            write_error_message(f"Secondary output path '{secondary_output_path}' does not exist")
            return False

        return True

    except Exception as e:
        write_error(e)
        return False


class export_processor:
    _input_filename: str
    _input_filepath: str
    _input_directory: str
    _file_lines: List[str] = []
    _primary_output_directory: str
    _secondary_output_directory: str
    _convert_to_prompts: bool
    _duplicate_file: bool
    _change_to_filename: str
    _primary_output_filepath: str
    _secondary_output_filepath: str

    def __init__(self, input_filename: str):
        self._input_filename = input_filename
        self._input_directory = get_stored_ini_value("Paths", "input_path", "settings")
        self._input_filepath = os.path.join(self._input_directory, input_filename)
        self._file_lines = get_unencoded_file_lines(self._input_filepath)
        self._primary_output_directory = str(get_stored_ini_value("Paths", "primary_output_path", "settings"))
        self._secondary_output_directory = get_stored_ini_value("Paths", "secondary_output_path", "settings")
        self._convert_to_prompts = bool(get_stored_ini_value("ProcessSwitches", "convert_text_to_prompt", "settings"))
        self._duplicate_file = bool(get_stored_ini_value("ProcessSwitches", "duplicate_file", "settings"))
        self._change_to_filename = get_stored_ini_value("ProcessSwitches", "change_to_filename", "settings")
        self._primary_output_filepath = str(os.path.join(self._primary_output_directory, input_filename))
        self._secondary_output_filepath = str(os.path.join(self._secondary_output_directory, self._change_to_filename))

    def _replace_text_with_prompt(self, search_text, current_text, replacement_text) -> bool:
        idx = get_index_containing_text(self._file_lines, search_text)
        if idx != -1:
            line = self._file_lines[idx]
            self._file_lines[idx] = line.replace(current_text, replacement_text)
            return True
        else:
            return False

    def _format_export_file(self):

        if any([self._replace_text_with_prompt("Text EMPLOYEE", "Text EMPLOYEE: Text", "Prompt EMPLOYEE: Input"),
                self._replace_text_with_prompt("Text JOB", "Text JOB: Text", "Prompt JOB: Input"),
                self._replace_text_with_prompt("Text MACHINE", "Text MACHINE: Text", "Prompt MACHINE: Input"),
                self._replace_text_with_prompt("Text SEQUENCE", "Text SEQUENCE: Text", "Prompt SEQUENCE: Input")]):
            write_lines_to_file(self._input_filepath, self._file_lines)

    def _extract_rev_letter(self) -> str:
        idx = get_index_containing_text(self._file_lines, "Text REV LETTER:")
        line = self._file_lines[idx]
        return line.split(",")[1].strip("\n").strip("\"")

    def _generate_spc_part_number_line(self, current_line: str) -> str:
        first_part = current_line.split(",")[1].strip("\n").strip("\"")
        second_part = self._extract_rev_letter()
        return f"\"{first_part} REV {second_part}\"\n"

    def _convert_export_to_spc_style(self):
        idx = get_index_containing_text(self._file_lines, "Text PT")
        line = self._file_lines[idx]
        self._file_lines[idx] = self._generate_spc_part_number_line(line)

        idx = get_index_containing_text(self._file_lines, "Prompt EMPLOYEE")
        line = self._file_lines[idx]
        self._file_lines[idx] = line.split(",")[1]

        idx = get_index_containing_text(self._file_lines, "Prompt JOB")
        line = self._file_lines[idx]
        self._file_lines[idx] = line.split(",")[1]

        idx = get_index_containing_text(self._file_lines, "Prompt MACHINE")
        line = self._file_lines[idx]
        self._file_lines[idx] = line.split(",")[1]

        idx = get_index_containing_text(self._file_lines, "Text IN PROCESS")
        line = self._file_lines[idx]
        self._file_lines[idx] = line.split(",")[1].replace("IN PROCESS", "RUN")

        idx = get_index_containing_text(self._file_lines, "Text REV LETTER:")
        self._file_lines.pop(idx)

        idx = get_index_containing_text(self._file_lines, "Text OPERATION:")
        self._file_lines.pop(idx)

        idx = get_index_containing_text(self._file_lines, "Prompt SEQUENCE:")
        self._file_lines.pop(idx)

        for i, l in enumerate(self._file_lines):
            self._file_lines[i] = l.replace(",", "\t").replace("\n", "\t\n").replace("\t\t", "\t")

        write_lines_to_file(self._input_filepath, self._file_lines)

    def process_export(self):
        try:
            if self._convert_to_prompts:
                self._format_export_file()
            if self._duplicate_file:
                shutil.copyfile(self._input_filepath, self._primary_output_filepath)
                self._convert_export_to_spc_style()
                shutil.move(self._input_filepath, self._secondary_output_filepath)
            else:
                shutil.move(self._input_filepath, self._primary_output_filepath)
        except Exception as e:
            write_error(e)


def main():
    if check_file_paths():
        input_directory = get_stored_ini_value("Paths", "input_path", "settings")
        while True:
            for filename in os.listdir(input_directory):
                time.sleep(6)
                export = export_processor(filename)
                export.process_export()
                print(filename)


if __name__ == "__main__":
    main()
