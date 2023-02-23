from typing import Dict
import uuid
import requests as r

BASE_URL = "https://sandbox.api.service.nhs.uk/spine-directory/FHIR/R4"
DEVICE_URL = f"{BASE_URL}/Device"
ENDPOINT_URL = f"{BASE_URL}/Endpoint"

SERVICE_INTERACTION_ID_STRUCTURED = "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:psis:REPC_IN150016UK05" # this is for sandbox purposes it will be replaced with the official one
API_KEY = "123" # this is for sandbox purposes it will be replaced with the official one

def get_sds_device_data(ods_code):
    """Retrieves the whole response from the /Device endpoint"""

    ORG = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods_code}"
    device_payload = {"organization": ORG, "identifier": [SERVICE_INTERACTION_ID_STRUCTURED]}
    device_headers = {"X-Correlation-Id": uuid.uuid4(), "apikey": API_KEY} # API reference doesn't specify uuid as a str
    
    try:
        device_req = r.get(url=DEVICE_URL,
            params=device_payload,
            headers=device_headers)
        device_req.raise_for_status()
        resp_json = device_req.json()
    except r.exceptions.HTTPError as errh:
        print ("Http Error:",errh)
        resp_json = {"error": errh}
    except r.exceptions.ConnectionError as errc:
        print ("Error Connecting:",errc)
        resp_json = {"error": errc}
    except r.exceptions.Timeout as errt:
        print ("Timeout Error:",errt)
        resp_json = {"error": errt}
    except r.exceptions.RequestException as err:
        print ("Something Else",err)
        resp_json = {"error": err}

    return resp_json

device_body = get_sds_device_data()

def extract_nhsMhsPartyKey(body=device_body):
    """Extracts the nhsPartyKey value from the /Device of SDS FHIR API response"""
   
    party_key = body["entry"][0]["resource"]["identifier"][1]["value"]
    return party_key


def extract_asid(body=device_body):
    """Extracts the ASID value from the /Device of SDS FHIR API response"""
    
    asid_number = body["entry"][0]["resource"]["identifier"][0]["value"]
    return asid_number

def get_sds_endpoint_data(nhsMhsPartyKey):
    """Retrieves the whole response from the /Endpoint endpoint"""
    nhsMhsPartyKey = extract_nhsMhsPartyKey()

    SERVICE_INTERACTION_ID_PARTY_KEY = f"https://fhir.nhs.uk/Id/nhsMhsPartyKey|{nhsMhsPartyKey}"

    device_payload = {"identifier": [SERVICE_INTERACTION_ID_STRUCTURED, SERVICE_INTERACTION_ID_PARTY_KEY]}
    device_headers = {"X-Correlation-Id": uuid.uuid4(), "apikey": API_KEY} # API reference doesn't specify uuid as a str

    endpoint_req = r.get(url=ENDPOINT_URL,
                params=device_payload,
                headers=device_headers)
    return endpoint_req.json()

endpoint_body = get_sds_endpoint_data()

def extract_adress(body=endpoint_body):
    """Extracts the address value from the /Endpoint of SDS FHIR API response"""
    address = body["entry"][0]["resource"]["address"]
    return address

def handler(event, _context) -> Dict:
    """
    Invokes a lambda
    """
    
    return {
        "statusCode": "all good",
        "body": {
            "result": extract_adress(),
            "message": "This is sds"
        },
    }