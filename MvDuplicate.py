import os
import shutil
import time
from typing import List

from lib.Utilities import (get_stored_ini_value, get_unencoded_file_lines,
                           write_lines_to_file, get_index_containing_text)


class export_processor:
    _input_filename:str
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

        write_lines_to_file(self._input_filepath, self._file_lines)

    def process_export(self):
        if self._convert_to_prompts:
            self._format_export_file()
        if self._duplicate_file:
            shutil.copyfile(self._input_filepath, self._primary_output_filepath)
            self._convert_export_to_spc_style()
            shutil.move(self._input_filepath, self._secondary_output_filepath)
        else:
            shutil.move(self._input_filepath, self._primary_output_filepath)


def main():
    while True:
        input_directory = get_stored_ini_value("Paths", "input_path", "settings")
        for filename in os.listdir(input_directory):
            export = export_processor(filename)
            export.process_export()
            time.sleep(6)


if __name__ == "__main__":
    main()
