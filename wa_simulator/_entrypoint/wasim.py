"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Command imports
import wa_simulator._entrypoint.docker as docker

# Utility imports
from wa_simulator.utils import set_verbosity

# General imports
import argparse

def main():
    # Main entrypoint and initialize the cmd method
    # set_defaults specifies a method that is called if that parser is used
    parser = argparse.ArgumentParser(description="WA Simulator Command Line Interface")
    parser.add_argument('-v', '--verbose', dest='verbosity', action='count', help='Level of verbosity', default=0)
    parser.add_argument('--dry_run', action="store_true", help="Run as a dry run")
    parser.set_defaults(cmd=lambda x: x)

    # Initialize the subparsers
    subparsers = parser.add_subparsers()
    docker.init(subparsers.add_parser("docker", description="Docker utilities for the WA Simulator"))  # noqa

    # Parse the arguments and update logging
    args = parser.parse_args()
    set_verbosity(args.verbosity)

    # Calls the cmd for the used subparser
    args.cmd(args)
