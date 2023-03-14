# pylint: disable=line-too-long, duplicate-code

import json
import time
import uuid
from http import HTTPStatus

import jwt
import requests

from .get_fhir_error import get_fhir_error


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


def ssp_html_request(org_fhir_url, org_asid, patient_nhs_number, write_log, integration_env=False):
    write_log(
        "SSP001",
        {
            "nhs_number": patient_nhs_number,
            "org_asid": org_asid,
            "org_fhir_endpoint": org_fhir_url,
            "type": "html",
        },
    )

    proxy_fqdn = "https://proxy.opentest.hscic.gov.uk/"
    structured_record_endpoint = "Patient/$gpc.getcarerecord"

    # The opentest endpoint for GpConnect 0.7.2 - Access Record HTML is just a sandbox
    # So none of the details we get back from SDS are relevant when calling it
    # Instead we just hardcode in the values here and wait until we're onboarded to the
    # integration environment
    if not integration_env:  # pragma: no cover
        org_fhir_url = "https://orange.testlab.nhs.uk/gpconnect-demonstrator/v0/fhir"
        org_asid = "918999198993"
        proxy_fqdn = ""

    url = f"{proxy_fqdn}{org_fhir_url}/{structured_record_endpoint}"

    headers = get_headers(patient_nhs_number, org_asid)
    body = get_request_body(patient_nhs_number)

    write_log("SSP002", {"url": url, "headers": headers, "body": body})

    try:
        response = requests.post(
            url,
            headers=headers,
            data=body,
            timeout=300,
        )
    except Exception as e:  # pylint: disable=broad-except
        write_log("SSP003", {"error": str(e)})
        return None, f"Exception in SSP request with error={str(e)}"

    if response.status_code == HTTPStatus.NOT_FOUND:
        write_log("SSP004", {"nhs_number": patient_nhs_number})
        return None, f"SSP failed to find patient with nhs_number={patient_nhs_number}"

    # In future will need to investigate the various response status codes and potentially
    # give a more useful error message to end user based on the particular code
    if response.status_code != HTTPStatus.OK:
        write_log(
            "SSP005",
            {
                "status_code": response.status_code,
                "response_content": get_fhir_error(response.json()),
            },
        )
        return None, f"SSP request returned non-200 status_code={response.status_code}"

    return response.json(), "Success"
