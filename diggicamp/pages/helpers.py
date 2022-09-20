def clean_name_for_fs(name: str):
    return name.strip().translate(str.maketrans({"/": "", "<": "", ">": "", ":": "", "\"": "", "\\": "", "?": "", "*": "", "|": ""}))