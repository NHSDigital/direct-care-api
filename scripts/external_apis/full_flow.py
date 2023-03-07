import os
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(SCRIPT_DIR))

from external_apis.pds_request import pds_fhir_lookup
from external_apis.sds_request import main
from external_apis.spine_secure_proxy_request import make_request

if __name__ == "__main__":
    nhs_number = sys.argv[1]
    ods_code = pds_fhir_lookup(nhs_number)
    asid, address = main(ods_code)
    ssp_response = make_request(address, asid, nhs_number)
    print(ssp_response)
