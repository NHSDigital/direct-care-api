"""
When the lambda function is createdmthe directory structure
changes slightly so whenever you need to access a file in
the python code, you need to get the absolute path of the *python* file that wants to use
that file, then navigate to the file relatively
"""

import os


def absolute_file_path(root, *paths):
    """Get the absolute file path"""
    return os.path.join(
        os.path.dirname(os.path.realpath(root)),
        *paths,
    )
