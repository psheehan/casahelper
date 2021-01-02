# Return a dictionary with the line information for the relevant lines.

def get_line_info(lines):
    # Dictionary of lines.

    lines_dictionary = {
        "13CO3-2":330.587965,
        "C18O3-2":329.330553,
        "CN3-2_72-52":340.247770,
        "CN3-2_52-32":340.031549,
        "CN3-2_52-52_7":339.516635,
        "CN3-2_52-52_3":339.446777,
        "CS7-6":342.882857
    }

    line_data = {}
    for line in lines:
        line_data = lines_dictionary[line]

    return line_data
