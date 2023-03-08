import configparser

SECTION_LEVEL = "Log Level"
SECTION_TEXT = "Log Text"


class LogbaseError(ValueError):
    """Exception to raise when the log config is incomplete"""


def parse_log_base(log_base_file):
    log_base_config = configparser.RawConfigParser()
    log_base_config.read(log_base_file)
    log_base_dict = {}
    for log_ref in log_base_config.sections():
        level = log_base_config.get(log_ref, SECTION_LEVEL)
        if not level:  # pragma: no cover
            raise LogbaseError(f"No level provided for Ref={log_ref}")
        text = log_base_config.get(log_ref, SECTION_TEXT)
        text += " - transactionId={transaction_id} userId={user_id} userOrgCode={user_org_code}"
        if not level:  # pragma: no cover
            raise LogbaseError(f"No text provided for Ref={log_ref}")

        log_base_dict[log_ref] = {"level": level, "text": text}

    return log_base_dict
