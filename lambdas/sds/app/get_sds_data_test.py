import unittest

from .sds.sds import extract_address, extract_asid, extract_nhsMhsPartyKey

# pylint: disable= line-too-long, invalid-name
class TestExtractionMethods(unittest.TestCase):
    """Tests the methods which extract data from the response bodies"""

    def test_extract_nhsMhsPartyKey(self):
        body = {"entry": [
        {
            "fullUrl": "http://sandbox.apis.ptl.api.platform.nhs.uk/Device/3E33F9AD-D856-4C02-9652-AADD3202D0F3",
            "resource": {
                "resourceType": "Device",
                "id": "3E33F9AD-D856-4C02-9652-AADD3202D0F3",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                        "value": "928942012545"
                    },
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey",
                        "value": "YES-0000806"
                    }
                ]}
        }]}
        actual = "YES-0000806"
        expected = extract_nhsMhsPartyKey(body)
        self.assertEqual(actual, expected)

    def test_donot_extract_wrong_nhsMhsPartyKey(self):
        body = {"entry": [
        {
            "fullUrl": "http://sandbox.apis.ptl.api.platform.nhs.uk/Device/3E33F9AD-D856-4C02-9652-AADD3202D0F3",
            "resource": {
                "resourceType": "Device",
                "id": "3E33F9AD-D856-4C02-9652-AADD3202D0F3",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                        "value": "928942012545"
                    },
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey",
                        "value": "YES-0000806"
                    }
                ]}
        }]}
        actual = "YES-0000807"
        expected = extract_nhsMhsPartyKey(body)
        self.assertNotEqual(actual, expected)

    def test_donot_extract_empty_nhsMhsPartyKey(self):
        body = {"entry": []}
        with self.assertRaises(IndexError):
            extract_nhsMhsPartyKey(body)

    def test_extract_asid(self):
        body = {"entry": [
        {
            "fullUrl": "http://sandbox.apis.ptl.api.platform.nhs.uk/Device/3E33F9AD-D856-4C02-9652-AADD3202D0F3",
            "resource": {
                "resourceType": "Device",
                "id": "3E33F9AD-D856-4C02-9652-AADD3202D0F3",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                        "value": "928942012545"
                    },
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey",
                        "value": "YES-0000806"
                    }
                ]}
        }]}
        actual = "928942012545"
        expected = extract_asid(body)
        self.assertEqual(actual, expected)

    def test_donot_extract_wrong_asid(self):
        body = {"entry": [
        {
            "fullUrl": "http://sandbox.apis.ptl.api.platform.nhs.uk/Device/3E33F9AD-D856-4C02-9652-AADD3202D0F3",
            "resource": {
                "resourceType": "Device",
                "id": "3E33F9AD-D856-4C02-9652-AADD3202D0F3",
                "identifier": [
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsSpineASID",
                        "value": "928942012545"
                    },
                    {
                        "system": "https://fhir.nhs.uk/Id/nhsMhsPartyKey",
                        "value": "YES-0000806"
                    }
                ]}
        }]}
        actual = "928942012546"
        expected = extract_asid(body)
        self.assertNotEqual(actual, expected)

    def test_donot_extract_empty_asid(self):
        body = {"entry": []}
        with self.assertRaises(IndexError):
            extract_asid(body)

    def test_extract_adress(self):
        body= {
            "entry" : [ {
                "fullUrl" : "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Endpoint/08CE3BFB-5055-422B-9AE5-80DF6F4E1C61",
                "resource" : {
                "resourceType" : "Endpoint",
                "id" : "08CE3BFB-5055-422B-9AE5-80DF6F4E1C61",
                "status" : "active",
                "connectionType" : {
                    "system" : "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                    "code" : "hl7-fhir-msg",
                    "display" : "HL7 FHIR Messaging"
                },
                "payloadType" : [ {
                    "coding" : [ {
                    "system" : "http://terminology.hl7.org/CodeSystem/endpoint-payload-type",
                    "code" : "any",
                    "display" : "Any"
                    } ]
                } ],
                "address" : "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest",
                }
            }
        ]
    }
        actual = "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest"
        expected = extract_address(body)
        self.assertEqual(actual, expected)

    def test_donot_extract_wrong_adress(self):
        body= {
            "entry" : [ {
                "fullUrl" : "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Endpoint/08CE3BFB-5055-422B-9AE5-80DF6F4E1C61",
                "resource" : {
                "resourceType" : "Endpoint",
                "id" : "08CE3BFB-5055-422B-9AE5-80DF6F4E1C61",
                "status" : "active",
                "connectionType" : {
                    "system" : "http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
                    "code" : "hl7-fhir-msg",
                    "display" : "HL7 FHIR Messaging"
                },
                "payloadType" : [ {
                    "coding" : [ {
                    "system" : "http://terminology.hl7.org/CodeSystem/endpoint-payload-type",
                    "code" : "any",
                    "display" : "Any"
                    } ]
                } ],
                "address" : "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliablerequest",
                }
            }
        ]
    }
        actual = "https://msg.int.spine2.ncrs.nhs.uk/reliablemessaging/reliabler"
        expected = extract_address(body)
        self.assertNotEqual(actual, expected)

    def test_donot_extract_empty_address(self):
        body = {"entry": []}
        with self.assertRaises(IndexError):
            extract_address(body)
