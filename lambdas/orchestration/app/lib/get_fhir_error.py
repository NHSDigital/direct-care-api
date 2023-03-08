from .get_dict_value import get_dict_value


def get_fhir_error(record):
    """Return error description from PDS response"""
    display = get_dict_value(record, "/issue/0/details/coding/0/display", default="Unknown error")
    diagnostics = get_dict_value(record, "/issue/0/diagnostics", default="No diagnostics available")
    return f"{display} - {diagnostics}"
