"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Imports from wa_simulator
from wa_simulator.utils import YAMLParser, LOGGER

# General imports
import argparse
import pathlib

def run_start(args):
    """The start command will spin up a Docker container that runs a python script with the desired image.

    The use case for the start command is when we'd like to run a :code:`wa_simulator` script with a certain
    operating system configuration or in a way that's distributable across computers. Everyone's setup is different,
    i.e. OS, development environment, packages installed. Using Docker, you can simply run :code:`wasim docker start ...`
    and run :code:`wa_simulator` agnostic from your local system.

    The start command will take two arguments that point to two files: 
    a YAML configuration file and the python script. The YAML file defines various settings we'll
    use when spinning up the container. The python script is the actual file we'll run from within the
    container. After the python script, you may add arguments that will get passed to the script
    when it's run in the container. See some examples below.

    YAML Settings:
        *   :code:`containers` (required): A list of containers we'd like to spin up. Each container is run sequentially (one after another; i.e. the previous container will complete before the next is run). Each container is idenified by a name, which is used as the container name.

        * :code:`image` (required): The image the container will use. If the image has not been downloaded, it will be fetched at runtime.

        * :code:`volumes` (optional): The `volumes <https://docs.docker.com/storage/volumes/>_` mapped from the host to the container. They can be specified either through a dictionary with :code:`host`, :code:`container`, and optionally :code:`is_relative_to_yaml` attributes. :code:`host` and :code:`container` are the paths from the host and container that make up the volume, respectively. :code:`is_relative_to_yaml` specified whether the :code:`host` path is relative to the yaml configuration file; if it is, the :code:`host` path will be resolved relative to the yaml file location (as Docker requires the host directory to be absolute). They can also be specified via a string that follows the traditional volume representation in the Docker CLI (i.e. :code:`"/usr/local:/usr/local"). The passed python script is automatically configured to be a volume at :code:`/root/`.

        * :code:`ports` (optional): The `ports <https://docs.docker.com/config/containers/container-networking/#published-ports>_` to bind the container to. These are specified as a dictionary, where the keys are the ports to bind inside the container. The keys then map to a list of either integers or strings that define ports to bind to on the host side.

    Examples YAML files:

    .. highlight:: yaml
    .. code-block:: yaml
        
        # -------------
        # Example1.yaml
        # -------------

        containers:
            wasim:
                image: wiscauto/wa_simulator
                volumes:
                    - host: "../data"
                      container: "/root/data"
                      is_relative_to_yaml: True
                    - "/usr/local:/usr/local"
                ports: # Dictionary of {<container>: [<host>, ...]}
                    5555:
                      - 5555
                    
    Example cli commands:

    .. highlight:: bash
    .. code-block:: bash
        
        # Run from within wa_simulator/demos/bridge
        wasim docker start demo_bridge.yaml demo_bridge_server.py

        # With more verbosity
        wasim -vv docker start demo_bridge.yaml demo_bridge_server.py

        # With some script arguments
        wasim -vv docker start demo_bridge.yaml demo_bridge_server.py --step_size 2e-3
    """
    import docker

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

    # Grab the containers (will throw error if not present)
    containers = yaml_parser.get('containers')
    
    # Loop through each container and parse the config
    # Will then run the container
    LOGGER.debug(f"Parsing containers in the YAML file...")
    for name, config in containers.items():
        LOGGER.debug(f"Parsing container named '{name}'...")

        # Get the image (will throw error if not present)
        image = config.get('image')
        
        # Create the volumes
        volumes = []
        volumes.append(f"{absfile}:/root/{filename}") # The actual file
        for vol in config.get('volumes', []):
            volume = ""
            if isinstance(vol, str):
                volume = vol
            elif isinstance(vol, dict):
                is_relative_to_yaml = vol.get('is_relative_to_yaml', False)
                if is_relative_to_yaml:
                    host = str((pathlib.Path(yaml_file).parent / pathlib.Path(vol['host'])).resolve())
                else:
                    host = str(pathlib.Path(vol['host']).resolve())
                container = vol['container'] 
                make_absolute = vol.get('make_absolute', False)
                
                volume = f"{host}:{container}"
            volumes.append(volume)

        # Create the port mappings
        ports = config.get('ports', {})

        # Run the script
        LOGGER.info(f"Running '{cmd}' with the following settings:")
        LOGGER.info(f"\tImage: {image}")
        LOGGER.info(f"\tVolumes: {volumes}")
        LOGGER.info(f"\tPorts: {ports}")
        if not args.dry_run:

            # setup the signal listener to listen for the interrupt signal (ctrl+c)
            import signal, sys
            def signal_handler(sig, frame):
                LOGGER.info(f"Stopping container.")
                container.kill()
                sys.exit(0)
            signal.signal(signal.SIGINT, signal_handler)

            # Run the command
            client = docker.from_env()
            container = client.containers.run(image, "/bin/bash", volumes=volumes, ports=ports, detach=True, tty=True, name=name, auto_remove=True)
            result = container.exec_run(cmd)
            print(result.output.decode())


def init(subparser):
    """Initializer method for the :code:`docker` entrypoint.

    The entrypoint serves as a mechanism for running containers with :code:`wa_simulator`. It may be
    desireable to have a containerized system for running :code:`wa_simulator`; for instance, if a script
    requiries a certain package, the Docker image could be shipped without needing to install the package
    on a system locally. The scalability of using Docker over installing packages on a system is much greater.

    To see specific commands that are available, run the following command:

    .. highlight:: bash
    .. code-block:: bash

        wasim docker -h

    Current subcommands:
        * :code:`start`: Spins up a container and runs a python script in the created container.
    """
    LOGGER.debug("Running 'docker' entrypoint...")

    # Create some entrypoints for additional commands
    subparsers = subparser.add_subparsers(required=False)

    # Start subcommand
    start = subparsers.add_parser("start", description="Start up the WA Simulator in a Docker container")
    start.add_argument("yaml", help="YAML file with docker configuration")
    start.add_argument("script", help="The script to start up in the Docker container")
    start.add_argument("script_args", nargs=argparse.REMAINDER, help="The arguments for the [script]")
    start.set_defaults(cmd=run_start)
