#!/bin/bash
#
# This script should be run via curl:
#   sh -c "$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/config_conda_env.sh)"
# or via wget:
#   sh -c "$(wget -qO- https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/config_conda_env.sh)"
# or via fetch:
#   sh -c "$(fetch -o - https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/scripts/config_conda_env.sh)"
#

exit_error() {
	msg=$1
	if [ -z "$1" ]; then
		msg="Unknown Error"
	fi
	echo -e "\nScript exited with error: $msg"
	exit 1
}

exit_okay() {
	msg=$1
	if [ -z "$msg" ]; then
		msg="OK"
	fi
	echo -e "\nScript exitted: $msg"
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

ask_response() {
	msg=$1
	if [ -z "$msg" ]; then
		exit_error "Pass a message to the ask_okay function."
	fi

	read -p "$msg " RESP
	echo $RESP
}

# Verify the script was run on purpose
if ask_okay "Create new conda env"; then
	CREATE_NEW_CONDA_ENV=1
elif ask_okay "Update conda env"; then
	UPDATE_CONDA_ENV=1
else
	exit_okay
fi

# Common prerequisites
check_command curl # Curl

# Check operating system specific prerequisites
check_command uname
os=$(uname)

if [[ "$os" == "Darwin" ]]; then
	if ! check_command brew "1"; then
		if ask_okay "Install Homebrew package manager"; then
			echo "Installing Homebrew. May take a few minutes"
			wait 1
			/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
		else
			exit_error "You may be missing packages. Brew should be used to install these packages."
		fi
	fi
	if ! check_command conda "1"; then
		if ask_okay "Install Anaconda"; then
			echo "Installing Anaconda. May take a few minutes"
			wait 1
			brew install --cask anaconda
			[ -f /usr/local/anaconda3/bin/conda ] && /usr/local/anaconda3/bin/conda init 
			[ -f /usr/local/anaconda3/bin/conda ] && export PATH=$PATH:/usr/local/anaconda3/bin/
		else
			exit_error "conda command not found."
		fi
	fi
	brew list libomp >/dev/null || brew install libomp
elif [[ "$os" == "Linux" ]]; then
	check_command conda # Anaconda
else
	exit_error "Detected operating system is $os. Currently not supported."
fi

# Get the environment.yml file from github
env_file=$(curl -fsSL https://raw.githubusercontent.com/WisconsinAutonomous/wa_simulator/master/environment.yml)

# Check the name
name="wa"
if ! ask_okay "Environment name '$name' okay"; then
	name=$(ask_response "Environment name :: ")
fi

# Create the conda environment from the retrieved environment.yml file
tmpfile=temp_env.yml
echo "$env_file" >>$tmpfile
if [ -n "$CREATE_NEW_CONDA_ENV" ]; then
	conda env create --name=$name -f=$tmpfile
elif [ -n "$UPDATE_CONDA_ENV" ]; then
	conda env update --name=$name -f=$tmpfile
fi
rm -f $tmpfile
