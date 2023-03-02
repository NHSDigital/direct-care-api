"""Test log helper to determine if correct logs and details were logged"""
import io
import sys


class LogHelper:
    """Log Helper"""

    LOG_TEMPLATE = "\n===================== {} ========================\n{}\n"

    def __init__(self, test_name) -> None:
        self.captured_output = None
        self.captured_err_output = None
        self.test_name = test_name
        self.used_logs = set()  # type: ignore

    def set_stdout_capture(self):
        """Reset the stdout capture"""
        self.captured_output = io.StringIO()
        self.captured_err_output = io.StringIO()
        sys.stdout = self.captured_output
        sys.stderr = self.captured_err_output

    def clean_up(self, test_failed=False):
        """Clean up after use"""
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        # If test fails print logs for test
        if test_failed:
            logs = self.logged_trimmed() or ["No logs created"]
            print(self.LOG_TEMPLATE.format(self.test_name, "\n".join(logs)))

        self.captured_output.close()
        self.captured_err_output.close()

    def reset(self):
        """Reset the logs"""
        self.clean_up()
        self.set_stdout_capture()

    def was_logged(self, log_reference):
        """Was a particular log reference logged"""
        if any(f"Ref={log_reference}" in line for line in self.logged):
            return True
        return False

    @property
    def logged(self):
        """
        Returns a list of the logs to give more information if log wasn't present
        """
        return self._get_log_lines()

    def logged_trimmed(self):
        """
        Returns trimmed logs for use in debugging tests
        """
        return [self.trim_log(idx, log) for idx, log in enumerate(self._get_log_lines(), start=1)]

    @staticmethod
    def trim_log(idx, log):
        """
        Trims unimportant noise from logs for debugging
        Before: [Date] [Timestamp] [Loglevel] [Process] [Logreference] [Message] [session_id]
        After: [OrderLogged] [Logreference] [Message]
        e.g -- 1. CAP0001 - Recaptcha endpoint called with token=12345678 secretPresent=True
        """
        trimmed_log = log
        try:
            trimmed_log = log.split("Ref=")[1]
        except IndexError:
            pass
        # trimmed_log = trimmed_log.split("- session_id")[0]
        trimmed_log = str(idx) + ". " + trimmed_log
        return trimmed_log

    def was_value_logged(self, log_reference, key, value):
        """Was a particular key-value pair logged for a log reference"""
        for log_line in self.logged:
            if f"Ref={log_reference}" not in log_line:
                continue

            if f"{key}={value}" in log_line or f'{key}="{value}"' in log_line:
                return True

        return False

    def logged_number_of_times(self, log_reference, number):
        """Was value logged the given number of times"""
        results = 0
        for log_line in self.logged:
            if f"Ref={log_reference}" in log_line:
                results += 1

        return results == number

    def _get_log_lines(self):
        """Get the logs lines"""
        return [
            log_line
            for log_line in self.captured_output.getvalue().split("\n")
            if log_line and "Ref" in log_line
        ]
