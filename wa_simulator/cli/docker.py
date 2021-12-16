"""
Wisconsin Autonomous - https://wa.wisc.edu

Copyright (c) 2021 wa.wisc.edu
All rights reserved.

Use of this source code is governed by a BSD-style license that can be found
in the LICENSE file at the top level of the repo
"""

# Imports from wa_simulator
from wa_simulator.utils import LOGGER
from wa_simulator.utils import _load_json, _check_field, _file_exists

# General imports
import argparse
import pathlib


def run_start(args):
    """The start command will spin up a Docker container that runs a python script with the desired image.

    The use case for the start command is when we'd like to run a :code:`wa_simulator` script with a certain
    operating system configuration or in a way that's distributable across computers. Everyone's setup is different,
    i.e. OS, development environment, packages installed. Using Docker, you can simply run :code:`wasim docker start ...`
    and run :code:`wa_simulator` agnostic from your local system.

    The start command requires one argument: a python script to run in the container.
    The python script is the actual file we'll run from within the
    container. After the python script, you may add arguments that will get passed to the script
    when it's run in the container.

    Optionally, you may provide a JSON configuration file. The JSON file defines various settings we'll
    use when spinning up the container. If a JSON configuration file is not provided, you must pass these options
    via the command line. There are many default values, so not all configurations are necessarily needed through
    the command line.

    JSON Settings:
        *   :code:`Container Name` (str, optional): Identifies the name that should be used for the container. If no name is passed, JSON will provide one. Defaults to "wasim-docker".

        * :code:`Image` (str, optional): The image the container will use. If the image has not been downloaded, it will be fetched at runtime. Defaults to "wiscauto/wa_simulator:latest".

        * :code:`Data` (list, optional): The folder that has all of the data files that will be used in the simulation. If you're familiar with docker, these will become `volumes <https://docs.docker.com/storage/volumes/>_`. By default, no volumes will be created if ``Data`` is left empty. Each entry in the ``Data`` list will be made a ``volumes`` and may have the following attributes:

            * ``Host Path`` (str, required): The path to the local folder that will be copied to the container. If ``Host Path Is Relative To JSON`` is not set to True (see below), it will be assumed as a global path

            * ``Host Path Is Relative To JSON`` (bool, optional): If set to True, the ``Host Path`` entry will be evaluated as if it were relative to the location of the JSON file provided. Defaults to False.

            * ``Container Path`` (str, optional): The path in the container to link the host path to. Defaults to ``/root/<file/folder name>``.

        * :code:`Port` (str, optional): The port to expose between the docker container and the host machine. This is the port that the server and client may communicate over. Ensure this is consistent with both your server and client code, as this will be the only port exposed. Default is 5555.

        * :code:`Network` (dict, optional): The network that the container should use for communication. See Docker `networks <https://docs.docker.com/network>_`. The ``Network`` dict must include a ``Name``, representing the name of the network, and optionally an ``IPv4`` field, representing the static ip to assign to the container. If no ``IPv4`` field is provided, a default value of 172.20.0.3 will be used. Further, if a network must be created because ``Name`` hasn't been created, the submask will be generated from ``IPv4``.

    Example JSON file:

    .. highlight:: javascript
    .. code-block:: javascript

        {
            "Name": "Demo bridge",
            "Type": "Bridge",

            "Container Name": "wasim-docker",
            "Image": "wiscauto/wa_simulator:latest",
            "Data": [
                {
                    "Path": "../data",
                    "Path Is Relative To JSON": true
                }
            ],
            "Network": {
                "Name": "wa",
                "IPv4": "172.30.0.3"
            }
        }

    Example cli commands:

    .. highlight:: bash
    .. code-block:: bash

        # ---------
        # With JSON
        # ---------

        # Run from within wa_simulator/demos/bridge
        wasim docker start --json demo_bridge.json demo_bridge_server.py

        # With more verbosity
        wasim -vv docker start --json demo_bridge.json demo_bridge_server.py

        # With some script arguments
        wasim -vv docker start --json demo_bridge.json demo_bridge_server.py --step_size 2e-3

        # ------------
        # Without JSON
        # ------------

        # Run from within wa_simulator/demos/bridge
        # Running wa_simulator/demos/bridge/demo_bridge_server.py using command line arguments rather than json
        # This should be used to communicate with a client running on the host
        wasim docker start \\
                --name wasim-docker \\
                --image wiscauto/wa_simulator \\
                --data "../data:/root/data" \\
                --data "/usr/local:/usr/local" \\ # Each entry serves as a new volume
                --port "5555:5555" \\
                demo_bridge_server.py --step_size 2e-3

        # Running wa_simulator/demos/bridge/demo_bridge_server.py using command line arguments rather than json
        # This should be used to communicate with another client in a container
        wasim docker start \\
                --name wasim-docker \\
                --image wiscauto/wa_simulator \\
                --data "../data:/root/data" \\
                --data "/usr/local:/usr/local" \\ # Each entry serves as a new volume
                --network "wa" \\
                demo_bridge_server.py --step_size 2e-3

        # Same thing as above, but leverages defaults
        wasim -vv docker start demo_bridge_server.py --step_size 2e-3
    """
    import docker
    from docker.utils import convert_volume_binds
    from docker.utils.ports import build_port_bindings

    LOGGER.debug("Running 'docker start' entrypoint...")

    # Grab the args to run
    script = args.script
    script_args = args.script_args

    # Grab the file path
    absfile = pathlib.Path(script).resolve()
    _file_exists(absfile, throw_error=True)
    filename = absfile.name

    # Create the command
    cmd = f"python {filename} {' '.join(script_args)}"

    # First, populate a config dictionary with the command line arguments
    # Since we do this first, all of the defaults will be entered into the config dict
    # Then, if a json overrides the default, it can just override the dict
    # Further, if a command line argument is provided, it will just be added to the dict here
    # instead of the default
    config: dict = {}

    # Image
    config["name"] = args.name
    config["image"] = args.image

    # Data folders
    config["volumes"] = []
    config["volumes"].append(f"{absfile}:/root/{filename}")  # The actual python file # noqa
    config["volumes"].extend(convert_volume_binds(args.data))

    # Ports
    config["ports"] = {}
    if args.port != "":
        port = args.port if ":" in args.port else f"{args.port}:{args.port}"
        config["ports"] = build_port_bindings([port])

    # Networks
    config["network"] = args.network
    config["ip"] = args.ip

    # Now, parse the json if one is provided
    if args.json is not None:
        j = _load_json(args.json)

        # Validate the json file
        _check_field(j, "Type", value="Bridge")
        _check_field(j, "Container Name", field_type=str, optional=True)
        _check_field(j, "Image", field_type=str, optional=True)
        _check_field(j, "Data", field_type=list, optional=True)
        _check_field(j, "Port", field_type=str, optional=True)
        _check_field(j, "Network", field_type=dict, optional=True)

        # Parse the json file
        config["name"] = j.get("Container Name", args.name)
        config["image"] = j.get("Image", args.image)

        if "Data" in j:
            for data in j["Data"]:
                # Validate the data
                _check_field(data, "Host Path", field_type=str)
                _check_field(data, "Host Path Is Relative To JSON",
                             field_type=bool, optional=True)
                _check_field(data, "Container Path",
                             field_type=bool, optional=True)

                # Create the volume string
                host = data["Host Path"]
                relative_to_json = data.get("Host Path", False)
                container = data.get("Container Path",
                                     f"/root/{pathlib.PurePath(host).name}")

                if relative_to_json:
                    host = str((pathlib.Path(args.json).parent /
                               pathlib.Path(host)).resolve())
                else:
                    host = str(pathlib.Path(host).resolve())

                config["volumes"].append(f"{host}:{container}")

        if "Port" in j:
            port = j["Port"]
            config["ports"] = build_port_bindings([f"{port}:{port}"])

        if "Network" in j:
            n = j["Network"]

            # Validate the network
            _check_field(n, "Name", field_type=str)
            _check_field(n, "IP", field_type=str, optional=True)

            config["network"] = n["Name"]
            config["ip"] = n.get("IP", args.ip)

    # Run the script
    LOGGER.info(f"Running '{cmd}' with the following settings:")
    LOGGER.info(f"\tImage: {config['image']}")
    LOGGER.info(f"\tVolumes: {config['volumes']}")
    LOGGER.info(f"\tPorts: {config['ports']}")
    LOGGER.info(f"\tNetwork: {config['network']}")
    LOGGER.info(f"\tIP: {config['ip']}")
    if not args.dry_run:
        try:
            # Get the client
            client = docker.from_env()

            # setup the signal listener to listen for the interrupt signal (ctrl+c)
            import signal
            import sys

            def signal_handler(sig, frame):
                if running_container is not None:
                    LOGGER.info(f"Stopping container.")
                    running_container.kill()
                sys.exit(0)
            signal.signal(signal.SIGINT, signal_handler)

            # Check if image is found locally
            running_container = None
            try:
                client.images.get(config["image"])
            except docker.errors.APIError as e:
                LOGGER.warn(
                    f"{config['image']} was not found locally. Pulling from DockerHub. This may take a few minutes...")
                client.images.pull(config["image"])
                LOGGER.warn(
                    f"Finished pulling {config['image']} from DockerHub. Running command...")

            # Check if network has been created
            if config["network"] != "":
                try:
                    client.networks.get(config["network"])
                except docker.errors.NotFound as e:
                    LOGGER.warn(
                        f"{config['network']} has not been created yet. Creating it...")

                    import ipaddress
                    network = ipaddress.ip_network(
                        f"{config['ip']}/255.255.255.0", strict=False)
                    subnet = str(list(network.subnets())[0])

                    ipam_pool = docker.types.IPAMPool(subnet=subnet)
                    ipam_config = docker.types.IPAMConfig(pool_configs=[ipam_pool])

                    LOGGER.info(
                        f"Creating network with name '{config['network']}' with subnet '{subnet}'.")
                    client.networks.create(
                        name=config["network"], driver="bridge", ipam=ipam_config)

            # Run the command
            running_container = client.containers.run(
                config["image"], "/bin/bash", volumes=config["volumes"], ports=config["ports"], remove=True, detach=True, tty=True, name=config["name"], auto_remove=True)
            if config["network"] != "":
                client.networks.get(config["network"]).connect(running_container, ipv4_address=config["ip"]) # noqa
            result = running_container.exec_run(cmd)
            print(result.output.decode())
            running_container.kill()
        except Exception as e:
            if running_container is not None:
                running_container.kill()

            raise e


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
    start = subparsers.add_parser(
        "start", description="Start up the WA Simulator in a Docker container")
    start.add_argument(
        "--json", type=str, help="JSON file with docker configuration", default=None)
    start.add_argument("--name", type=str,
                       help="Name of the container.", default="wasim-docker")
    start.add_argument("--image", type=str, help="Name of the image to run.",
                       default="wiscauto/wa_simulator:latest")
    start.add_argument("--data", type=str, action="append",
                       help="Data to pass to the container as a Docker volume. Multiple data entries can be provided.", default=[])
    start.add_argument("--port", type=str,
                       help="Ports to expose from the container.", default="")
    start.add_argument("--network", type=str,
                       help="The network to communicate with.", default="")
    start.add_argument("--ip", type=str,
                       help="The static ip address to use when connecting to 'network'. Used as the server ip.", default="172.20.0.3")
    start.add_argument(
        "script", help="The script to start up in the Docker container")
    start.add_argument("script_args", nargs=argparse.REMAINDER,
                       help="The arguments for the [script]")
    start.set_defaults(cmd=run_start)
