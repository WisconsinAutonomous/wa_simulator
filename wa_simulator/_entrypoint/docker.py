"""
Wisconsin Autonomous - https://www.wisconsinautonomous.org

Copyright (c) 2021 wisconsinautonomous.org
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Imports from wa_simulator
from wa_simulator.utils import YAMLParser, LOGGER

# General imports
import docker
import argparse
import pathlib

def run_start(args):
    LOGGER.debug("Running 'docker start' entrypoint...")
    
    # Grab the args to run
    script = args.script
    script_args = args.script_args

    # Grab the file path
    absfile = pathlib.Path(script).resolve()
    filename = absfile.name

    # Create the command
    cmd = f"python {filename} {' '.join(script_args)}"

    # Load the yaml file
    yaml_file = str(pathlib.Path(args.yaml).resolve())
    yaml_parser = YAMLParser(yaml_file)

    # Loop through each container and parse the config
    # Will then run the container
    LOGGER.debug(f"Parsing containers in the YAML file...")
    containers = yaml_parser.get('containers')
    for container, config in containers.items():
        LOGGER.debug(f"Parsing container named '{container}'...")

        # Get the image
        image = config.get('image')
        
        # Create the volumes
        volumes = []
        volumes.append(f"{absfile}:/root/{filename}") # The actual file
        for vol in config.get('volumes', []):
            volume = ""
            if isinstance(vol, str):
                volume = vol
            elif isinstance(vol, dict):
                is_relative_to_yaml_file = vol.get('is_relative_to_yaml_file', False)
                if is_relative_to_yaml_file:
                    host = str((pathlib.Path(yaml_file).parent / pathlib.Path(vol['host'])).resolve())
                else:
                    host = str(pathlib.Path(vol['host']).resolve())
                container = vol['container'] 
                make_absolute = vol.get('make_absolute', False)
                
                volume = f"{host}:{container}"
            volumes.append(volume)
            print(volumes)

        ports = config.get('ports', {})

        # Run the script
        LOGGER.info(f"Running '{cmd}'")
        if not args.dry_run:
            client = docker.from_env()
            container = client.containers.run(image, cmd, volumes=volumes, ports=ports, stdout=True, stderr=True)
            print(container)

def init(subparser):
    LOGGER.debug("Running 'docker' entrypoint...")

    # Create some entrypoints for additional commands
    subparsers = subparser.add_subparsers(required=False)

    # Start subcommand
    start = subparsers.add_parser("start", description="Start up the WA Simulator in a Docker container")
    start.add_argument("yaml", help="YAML file with docker configuration")
    start.add_argument("script", help="The script to start up in the Docker container")
    start.add_argument("script_args", nargs=argparse.REMAINDER, help="The arguments for the [script]")
    start.set_defaults(cmd=run_start)
