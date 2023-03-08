import dpath  # type: ignore


def get_dict_value(obj, path, default=None):
    """Get the value from the diction using the path provided"""
    try:
        return dpath.get(obj, path)
    except KeyError:
        return default
