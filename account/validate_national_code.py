import re


def is_valid_national_code(input):
    if not re.search(r'^\d{10}$', input):
        return False

    check = int(input[9])
    s = sum(map(lambda x: int(input[x]) * (10 - x), range(0, 9))) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)
