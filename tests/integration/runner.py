import argparse
import json
import os
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    # commandline arguments
    parser.add_argument(
        "--tags",
        required=False,
        help="Tags to include or exclude. use ~tag_name to exclude tags",
    )
    parser.add_argument(
        "--debug",
        required=False,
        action="store_true",
        help="Run in debug mode. The browser will not be headless and logging will be set to DEBUG",
    )
    argument = parser.parse_args()

    # Convert to behave commandline args
    tags = f" --tags {argument.tags} " if argument.tags else ""
    debug = " -D debug=True" if argument.debug else " -D debug=False"
    logging_level = "DEBUG" if argument.debug else "INFO"

    # complete command
    command = (
        f"behave{debug} -f behave_cucumber_formatter:PrettyCucumberJSONFormatter -o reports/cucumber_json.json"
        f" -f pretty tests/integration/features"
        f" --no-logcapture --logging-level={logging_level}{tags}"
    )
    print(f"Running subprocess with command: '{command}'")
    try:
        process = subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        raise e
    finally:
        pass
        # with open("results/behave_json.json", mode="r") as behave_json:
        #     cucumber_json = behave2cucumber.convert(json.load(behave_json))
        #     os.makedirs(os.path.dirname("reports/"), exist_ok=True)
        #     with open("reports/cucumber_json.json", mode="w") as cucumber_json_report:
        #         cucumber_json_report.write(json.dumps(cucumber_json[0]))
