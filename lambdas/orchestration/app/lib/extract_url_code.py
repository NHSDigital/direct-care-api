from urllib.parse import urlparse


def extract_url_parts(url):
    """Function to extract the ODS CODE from the /Device endpoint url of the SDS call"""
    parsed_url = urlparse(url)
    query = parsed_url.query.split("&")[0]
    if "|" in query:
        extracted_part = query.split("|")[-1]
    elif "%7C" in query:
        extracted_part = query.split("%7C")[-1]
    else:
        raise IndexError("Wrong separator in url")

    return extracted_part
