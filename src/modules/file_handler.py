open_files = {}


def get_file(filename):
    if filename not in open_files:
        with open(filename, "w"):
            pass

        open_files[filename] = open(filename, "a")

    return open_files[filename]


def append_coordinates(filename, x, y):
    file = get_file(filename)
    try:
        file.write(f"{x} {y}\n")
    except:
        print("APPEND ERR")


def close_files():
    for file in open_files.values():
        file.close()
