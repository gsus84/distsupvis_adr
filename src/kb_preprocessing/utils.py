from typing import List
from dataclasses import dataclass


def extract_cvponline_file_data(
        in_filename: str, indices: List[int], cvp_data_class: dataclass):
    extracted_data = []
    with open(in_filename, "r") as in_file:
        for line in in_file:
            line = line.replace("\"", "")
            line = line.replace("\n", "")
            line_parts = line.split(sep="$")
            extracted_data.append(
                cvp_data_class(*[line_parts[i] for i in indices])
            )
    return extracted_data