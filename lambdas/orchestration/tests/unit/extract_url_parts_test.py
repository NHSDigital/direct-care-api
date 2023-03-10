import logging
from ...app.lib.extract_url_code import extract_url_parts

# pylint: disable= line-too-long, invalid-name


def test_extract_ods_code_length_3(caplog):
    caplog.set_level(logging.INFO)
    url = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Device?organization=https://fhir.nhs.uk/Id/ods-organization-code|YES&identifier=https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:rest:search:patient&identifier=https://fhir.nhs.uk/Id/nhsMhsPartyKey|A20047-821870&manufacturing-organization=https://fhir.nhs.uk/Id/ods-organization-code|X26"
    actual = extract_url_parts(url)
    expected = "YES"
    assert actual == expected


def test_extract_ods_code_length_6(caplog):
    caplog.set_level(logging.INFO)
    url = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Device?organization=https://fhir.nhs.uk/Id/ods-organization-code|A20047&identifier=https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:rest:search:patient&identifier=https://fhir.nhs.uk/Id/nhsMhsPartyKey|A20047-821870&manufacturing-organization=https://fhir.nhs.uk/Id/ods-organization-code|X26"
    actual = extract_url_parts(url)
    expected = "A20047"
    assert actual == expected


def test_extract_ods_code_length_(caplog):
    caplog.set_level(logging.INFO)
    url = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Device?organization=https://fhir.nhs.uk/Id/ods-organization-code%7CB82617&identifier=https://fhir.nhs.uk/Id/nhsServiceInteractionId%7Curn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1"
    actual = extract_url_parts(url)
    expected = "B82617"
    assert actual == expected
