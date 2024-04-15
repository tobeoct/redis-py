def is_int(value):
    if not value:
        return False
    return value.lstrip("-").lstrip("+").isnumeric()


def to_int(value):
    if not is_int(value):
        return False, 0
    return True, int(value)
