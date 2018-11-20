"""
Utility to call cloudformation command with args
"""

import logging
import platform
import subprocess
import sys

LOG = logging.getLogger(__name__)


def execute_command(command, args, template_file):
    LOG.debug("%s command is called", command)
    try:
        aws_cmd = 'aws' if platform.system().lower() != 'windows' else find_windows_command("aws.cmd", "aws.exe")

        args = list(args)
        if template_file:
            # Since --template-file was parsed separately, add it here manually
            args.extend(["--template-file", template_file])

        subprocess.check_call([aws_cmd, 'cloudformation', command] + args)
        LOG.debug("%s command successful", command)
    except subprocess.CalledProcessError as e:
        # Underlying aws command will print the exception to the user
        LOG.debug("Exception: %s", e)
        sys.exit(e.returncode)


def find_windows_command(*options):

    for cmd in options:
        try:
            subprocess.Popen([cmd])
            # No exception. Let's pick this
            return cmd
        except OSError:
            pass

    raise OSError("Unable to find AWS CLI installation under following names: {}".format(options))
