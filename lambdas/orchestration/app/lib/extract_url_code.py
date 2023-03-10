from urllib.parse import urlparse


def extract_url_parts(url):
    """Function to extract the ODS CODE from the /Device endpoint url of the SDS call"""
    parsed_url = urlparse(url)
    query = parsed_url.query.split("&")[0]
    if len(query) == 0:  # TO DO edit the index error to represent a more realistic result + tests
        raise IndexError
    elif "%7C" in query:
        extracted_part = query.split("%7C")[-1]
    else:
        extracted_part = query.split("|")[-1]

    return extracted_part
