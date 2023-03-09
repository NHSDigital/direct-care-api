# pylint: skip-file

"""
Script to ping the structured data endpoint on GP connect through Spine Secure Proxy

Usage:
    python scripts/spine_secure_proxy_html.py <org_ods_code: from PDS> <org_asid: from SDS> <nhs_number: from original request>

For the default example use:
    python scripts/external_apis/spine_secure_proxy_html.py https://gpconnect-win1.itblab.nic.cfh.nhs.uk/B82617/STU3/1/gpconnect/structured/fhir 918999198993 9658218873

"""
import json
import sys
import time
import uuid

import dpath
import jwt
import requests


def get_unsigned_jwt_token(nhs_number, dcapi_ods_code="Y90705"):
    jwt_headers = {"alg": "none", "typ": "JWT"}
    jwt_payload = {
        "iss": "https://orange.testlab.nhs.uk/",
        "sub": "1",
        "aud": "https://authorize.fhir.nhs.net/token",
        "exp": int(time.time()) + 300,
        "iat": int(time.time()),
        "reason_for_request": "directcare",
        "requested_record": {
            "resourceType": "Patient",
            "identifier": [{"system": "http://fhir.nhs.net/Id/nhs-number", "value": nhs_number}],
        },
        "requested_scope": "patient/*.read",
        "requesting_device": {
            "resourceType": "Device",
            "id": "1",
            "identifier": [
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-system-instance-id",
                    "value": "gpcdemonstrator-0-orange",
                }
            ],
            "model": "GP Connect Demonstrator",
            "version": "0.7.2",
        },
        "requesting_organization": {
            "resourceType": "Organization",
            "id": "1",
            "identifier": [
                {"system": "http://fhir.nhs.net/Id/ods-organization-code", "value": dcapi_ods_code}
            ],
            "name": "Direct Care API",
        },
        "requesting_practitioner": {
            "resourceType": "Practitioner",
            "id": "1",
            "identifier": [
                {"system": "http://fhir.nhs.net/sds-user-id", "value": "G13579135"},
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-user-id",
                    "value": "1",
                },
            ],
            "name": {"family": ["Demonstrator"], "given": ["GPConnect"], "prefix": ["Mr"]},
            "practitionerRole": [
                {
                    "role": {
                        "coding": [
                            {
                                "system": "http://fhir.nhs.net/ValueSet/sds-job-role-name-1",
                                "code": "sds-job-role-name",
                            }
                        ]
                    }
                }
            ],
        },
    }
    return jwt.encode(jwt_payload, headers=jwt_headers, key="", algorithm="RS512")


def get_headers(nhs_number, org_asid, dcapi_asid="200000000359"):
    return {
        "Ssp-TraceID": str(uuid.uuid4()),
        "Ssp-From": dcapi_asid,
        "Ssp-To": org_asid,
        "Ssp-InteractionID": "urn:nhs:names:services:gpconnect:fhir:operation:gpc.getcarerecord",
        "Authorization": f"Bearer {get_unsigned_jwt_token(nhs_number)}",
        "accept": "application/json+fhir",
        "Content-Type": "application/json+fhir",
    }


def get_request_body(nhs_number):
    return json.dumps(
        {
            "resourceType": "Parameters",
            "parameter": [
                {
                    "name": "patientNHSNumber",
                    "valueIdentifier": {
                        "system": "http://fhir.nhs.net/Id/nhs-number",
                        "value": nhs_number,
                    },
                },
                {
                    "name": "recordSection",
                    "valueCodeableConcept": {
                        "coding": [
                            {
                                "system": "http://fhir.nhs.net/ValueSet/gpconnect-record-section-1",
                                "code": "ALL",
                            }
                        ]
                    },
                },
            ],
        }
    )


def make_request(org_fhir_url, org_asid, patient_nhs_number, integration_env=False):
    proxy_fqdn = "https://proxy.opentest.hscic.gov.uk/"
    structured_record_endpoint = "Patient/$gpc.getcarerecord"

    # The opentest endpoint for GpConnect 0.7.2 - Access Record HTML is just a sandbox
    # So none of the details we get back from SDS are relevant when calling it
    # Instead we just hardcode in the values here and wait until we're onboarded to the
    # integration environment
    if not integration_env:
        org_fhir_url = "https://orange.testlab.nhs.uk/gpconnect-demonstrator/v0/fhir"
        org_asid = "918999198993"
        proxy_fqdn = ""

    url = f"{proxy_fqdn}{org_fhir_url}/{structured_record_endpoint}"

    headers = get_headers(patient_nhs_number, org_asid)
    body = get_request_body(patient_nhs_number)

    response = requests.post(
        url,
        headers=headers,
        data=body,
        timeout=300,
    )

    print(dpath.get(response.json(), "/entry/0/resource/section/0/text/div"))


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

    make_request(ORG_FHIR_URL, ORG_ASID, PATIENT_NHS_NUMBER)  # type: ignore
