#!/usr/bin/env python3
"""
intel_gpu_top_telegraf

This is a simple script that executes intel_gpu_top with JSON output, which it then gently massages to
make it compatible with Telegraf's JSON input data format. It will pretty-print the valid JSON output string.
"""

import json
import logging
import subprocess
import sys
import time

# Initialize the logger
logger = logging.getLogger('intel_gpu_top_telegraf.py')
logging.basicConfig(level=logging.INFO)


def execute_intel_gpu_top() -> str:
    """
    execute_intel_gpu_top

    Runs the intel_gpu_top binary with JSON output (-J), lets it run for less than one second, then sends a SIGINT.
    It then parses the JSON string from stdout, converts it to a dictionary to inject a timestamp and measurement name,
    then it converts it back to JSON and returns the final, pretty-printed JSON string as output.
    """

    # Generic help text for failures to execute intel_gpu_top
    exec_failure_msg = 'Is the "intel-gpu-tools" package installed? Did you run the process with root privileges \
(required)? Have you been eating your vegetables?'

    # Run the intel_gpu_top process with JSON output enabled
    top = subprocess.Popen(['intel_gpu_top', '-J'], stdout=subprocess.PIPE, text=True)

    # The sampling interval for intel_gpu_top is 1s, so sleep for a half second to ensure we only ever get one sample
    time.sleep(0.5)

    # Send a SIGINT (2) to the intel_gpu_top process, which causes it to exit gracefully and close the JSON body
    top.send_signal(2)

    # Write some process details to variables
    out, err = top.communicate(timeout=3)
    cmd = top.args
    rc = top.returncode

    # Make sure stdout was not empty
    if out is None or len(out) == 0:
        logger.critical('No output received from "%s" or unable to execute the process. %s', cmd, exec_failure_msg)
        sys.exit(1)

    # Check to confirm whether the subprocess exited successfully before continuing
    if rc is None or rc != 0:
        logger.critical('"%s" exited non-zero (%s). %s\nOutput: %s\nErrors: %s', cmd, rc, exec_failure_msg, out, err)
        sys.exit(1)

    # Time to read the JSON and inject a timestamp + a measurement name
    json_dict = json.loads(out)
    if not isinstance(json_dict, list) or len(json_dict) == 0:
        logger.critical('Invalid JSON structure output from "%s". Expected a non-empty list, got: %s', cmd, out)
        sys.exit(1)
    json_dict[0].update({'timestamp':  time.time_ns(), 'measurement_name': 'intel_gpu_top'})
    json_output = json.dumps(json_dict[0], indent=4)

    return json_output


if __name__ == "__main__":
    # Get the JSON output from intel_gpu_top and make it Telegraf friendly, then send it to stdout
    print(execute_intel_gpu_top())
