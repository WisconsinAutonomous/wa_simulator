#!/bin/sh

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
	if [ -z "$cmd" ]; then
		exit_error "Pass a command to the check_command function."
	fi
	which $cmd >/dev/null || exit_error "$cmd not found. Install $cmd and try again."
}

ask_okay() {
	msg=$1
	if [ -z "$msg" ]; then
		exit_error "Pass a message to the ask_okay function."
	fi

	read -p "$msg ([y]/n)? " CONT
	case ${CONT:0:1} in
	y | Y | "") ;;

	*)
		exit_okay
		;;
	esac
}

# Verify the script was run on purpose
ask_okay "Create new conda env"

# Check operating system specific prerequisites
check_command uname
os=$(uname)

if [[ "$os" == 'Darwin' ]]; then
	# Check for prerequisites
	check_command brew # MacOS package manager
elif [[ "$os" == 'Linux' ]]; then
	echo ''
else
	exit_error "Detected operating system is $os. Currently not supported."
fi

# Common prerequisites
check_command conda # Anaconda
check_command wget  # Web Get

# Create the conda environment from the retrieved environment.yml file
