"""
Script to ping the structured data endpoint on GP connect through Spine Secure Proxy

Usage:
    python scripts/spine_secure_proxy_request.py <org_ods_code: from PDS> <org_asid: from SDS> <nhs_number: from original request>

For the default example use:
    python scripts/external_apis/spine_secure_proxy_request.py https://gpconnect-win1.itblab.nic.cfh.nhs.uk/B82617/STU3/1/gpconnect/structured/fhir 918999198738 9690937278

"""
import json
import sys
import time
import uuid
from urllib.parse import urlparse

import dpath
import jwt
import requests


def get_unsigned_jwt_token(dcapi_ods_code="Y90705"):
    jwt_headers = {"alg": "none", "typ": "JWT"}
    jwt_payload = {
        "iss": "https://orange.testlab.nhs.uk/",
        "sub": "1",
        "aud": "https://orange.testlab.nhs.uk/B82617/STU3/1/gpconnect/documents/fhir",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "reason_for_request": "directcare",
        "requested_scope": "patient/*.read",
        "requesting_device": {
            "resourceType": "Device",
            # Where do we get this from?
            "identifier": [
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-system-instance-id",
                    "value": "gpcdemonstrator-1-orange",
                }
            ],
            "model": "GP Connect Demonstrator",
            "version": "1.5.0",
        },
        "requesting_organization": {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": dcapi_ods_code,
                }
            ],
            # What name should we be using here
            "name": "Direct care API",
        },
        "requesting_practitioner": {
            "resourceType": "Practitioner",
            "id": "1",
            "identifier": [
                # This is from the demo and will need to be changed once we get to integration environments
                {
                    "system": "https://fhir.nhs.uk/Id/sds-user-id",
                    "value": "111111111111",
                },
                {
                    "system": "https://fhir.nhs.uk/Id/sds-role-profile-id",
                    "value": "22222222222222",
                },
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-user-id",
                    "value": "1",
                },
            ],
            "name": [{"family": "DIRECT CARE", "given": ["API"], "prefix": ["Dr"]}],
        },
    }
    return jwt.encode(jwt_payload, headers=jwt_headers, key="", algorithm="RS512")


def get_headers(org_asid, dcapi_asid="918999198232"):
    return {
        "Ssp-TraceID": str(uuid.uuid4()),
        "Ssp-From": dcapi_asid,
        "Ssp-To": org_asid,
        "Ssp-InteractionID": "urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1",
        "Authorization": f"Bearer {get_unsigned_jwt_token()}",
        "accept": "application/fhir+json",
        "Content-Type": "application/fhir+json",
    }


def get_request_body(nhs_number):
    return json.dumps(
        {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "patientNHSNumber",
                    "valueIdentifier": {
                        "system": "https://fhir.nhs.uk/Id/nhs-number",
                        "value": nhs_number,
                    },
                },
                {
                    "name": "includeAllergies",
                    "part": [
                        {"name": "includeResolvedAllergies", "valueBoolean": True}
                    ],
                },
                {"name": "includeMedication"},
                {
                    "name": "includeConsultations",
                    "part": [{"name": "includeNumberOfMostRecent", "valueInteger": 3}],
                },
                {"name": "includeProblems"},
                {"name": "includeImmunisations"},
                {"name": "includeUncategorisedData"},
                {"name": "includeInvestigations"},
                {"name": "includeReferrals"},
            ],
        }
    )


def make_request(org_fhir_url, org_asid, patient_nhs_number, integration_env=False):
    parsed_url = urlparse(org_fhir_url)
    structured_record_endpoint = "Patient/$gpc.getstructuredrecord"

    proxy_fqdn = "https://proxy.opentest.hscic.gov.uk/"

    # We're not yet onboarded into the integration environment for SSP / gpconnect  which means:
    # 1. The ASID returned from SDS for B82617 does not match the ASID on the test data on gpconnect
    # 2. The netloc of the 'address' field from SDS cannot be used with the gpconnect endpoint
    # 3. The sandbox SSP cannot be used as it requires VPN access to opentest
    if not integration_env:
        # Swap out the org ASID for the one that's in the gpconnect test data
        org_asid = "918999198738"
        # Remove the routing through the spine proxy
        proxy_fqdn = ""
        # Swap out the netloc for the one that's in the gpconnect test data
        parsed_url = parsed_url._replace(netloc="orange.testlab.nhs.uk")

    url = f"{proxy_fqdn}{parsed_url.geturl()}/{structured_record_endpoint}"

    headers = get_headers(org_asid)
    body = get_request_body(patient_nhs_number)

    response = requests.post(
        url,
        headers=headers,
        data=body,
        timeout=300,
    )

    print(dpath.get(response.json(), "entry/10/resource/name/0"))


if __name__ == "__main__":
    # First argument is ODS code of the organisation extracted from PDS request
    try:
        ORG_FHIR_URL = sys.argv[1]
    except IndexError:
        print("ORG fhir url from SDS must be provided as first argument")

    # Second argument is the organisation ASID extracted from SDS request
    try:
        ORG_ASID = sys.argv[2]
    except IndexError:
        print("ASID must be provided as second argument")

    # Third argument is the NHS number of the patient to look up taken from the
    # original query string parameter pass to the direct care api endpoint
    try:
        PATIENT_NHS_NUMBER = sys.argv[3]
    except IndexError:
        print("NHS number must be provided as third argument")

    make_request(ORG_FHIR_URL, ORG_ASID, PATIENT_NHS_NUMBER)
