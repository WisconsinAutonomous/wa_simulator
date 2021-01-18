#!/bin/sh
#
# This script should be run via curl:
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/create_conda_env.sh)"
# or via wget:
#   sh -c "$(wget -qO- https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/create_conda_env.sh)"
# or via fetch:
#   sh -c "$(fetch -o - https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/create_conda_env.sh)"
#

exit_error() {
	msg=$1
	if [ -z "$1" ]; then
		msg="Unknown Error"
	fi
	echo $'\n'"Script exited with error: $msg"
	exit 1
}

exit_okay() {
	msg=$1
	if [ -z "$msg" ]; then
		msg="OK"
	fi
	echo $'\n'"Script exitted: $msg"
	exit 0
}

check_command() {
	cmd=$1
	if [ -z "$2" ]; then
		which $cmd >/dev/null || exit_error "$cmd not found. Install $cmd and try again."
	else
		return $(which $cmd >/dev/null)
	fi
}

ask_okay() {
	msg=$1
	if [ -z "$msg" ]; then
		exit_error "Pass a message to the ask_okay function."
	fi

	read -p "$msg ([y]/n)? " CONT
	case ${CONT:0:1} in
	y | Y | "")
		return 0
		;;
	*)
		return -1
		;;
	esac
}

# Verify the script was run on purpose
if ask_okay "Create new conda env"; then
	CREATE_NEW_CONDA_ENV=1
elif ask_okay "Update new conda env"; then
	UPDATE_CONDA_ENV=1
else
	exit_okay
fi

# Common prerequisites
check_command curl # Curl

# Check operating system specific prerequisites
check_command uname
os=$(uname)

if [[ "$os" == 'Darwin' ]]; then
	if ! check_command brew "1" && ask_okay "Install Homebrew package manager"; then
		echo 'Installing Homebrew. May take a few minutes'
		wait 1
		/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
	fi
	if ! check_command conda "1" && ask_okay "Install Anaconda"; then
		echo 'Installing Anaconda. May take a few minutes'
		wait 1
		brew install --cask anaconda
	fi
	brew list libomp >/dev/null || brew install libomp
elif [[ "$os" == 'Linux' ]]; then
	check_command conda # Anaconda
else
	exit_error "Detected operating system is $os. Currently not supported."
fi

# Get the environment.yml file from github
env_file=$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/develop/environment.yml)

# Create the conda environment from the retrieved environment.yml file
tmpfile=temp_env.yml
echo "$env_file" >>$tmpfile
if [ -n "$CREATE_NEW_CONDA_ENV" ]; then
	conda env create -f=$tmpfile
elif [ -n "$UPDATE_CONDA_ENV" ]; then
	conda env update -f=$tmpfile
fi
rm -f $tmpfile
