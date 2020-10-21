#!/bin/bash

# MacOS WA Chrono Simulator Installation Script
# This script does the following:
#  - Installs brew
#  - Installs required packages
#  - Clones the wa_chrono_sim repo and its submodules
#  - Installs Chrono and it's modules
#  - Installs the required Chrono utilities

SCRIPT_NAME="$0" # Get the script name

exit_error() {
  echo -e "$SCRIPT_NAME exited with error: $1"
  exit 1
}

pretty_print() {
  printf "\n%b\n" "$1"
}

print_help() {
  echo -e "MacOS WA Chrono Simulator Installation Script"
  echo -e ""
  echo -e "Usage:"
  echo -e " $1 [OPTION...]"
  echo -e ""
  echo -e " -h | --help | -?\t: Print usage"
  echo -e ""
  echo -e "General Options:"
  echo -e ""
  echo -e " -c | --clone\t\t\t: Clone the wa_chrono_sim repo."
  echo -e "      --clone-non-recursive\t: Clone the wa_chrono_sim repo without cloning Chrono."
  echo -e "      --force-clone\t\t: Force the clone even if the repo is already in PATH or working directory tree."
  echo -e ""
  echo -e " -b | --build-chrono\t\t: Build the ProjectChrono simulator from source."
  echo -e "      --anaconda\t\t: Install PyChrono through anaconda (requires anaconda to be installed)"
  echo -e ""
  echo -e "Chrono Build Options:"
  echo -e " Only used if --build-chrono is flagged."
  echo -e ""
  echo -e " -ci | --irrlicht\t: Install Chrono with Irrlicht Module"
  echo -e " -cp | --pychrono\t: Install Chrono with PyChrono Module"
  echo -e " -cs | --sensor\t\t: Install Chrono with Sensor Module (currently unsupported on Mac b/c it requires a NVIDIA GPU)"
  echo -e " -cy | --synchrono\t: Install Chrono with the SynChrono Module"
  echo -e ""
}

ARCH=$(uname -s)          # Get the architecture type
REPO_NAME="wa_chrono_sim" # Set the repo name
USER_SHELL_PROFILE="~/.zshrc"

# This script is meant only for MacOS (Darwin) computers
# Exit if the current architecture isn't Darwin
if [ "$ARCH" != "Darwin" ]; then
  exit_error "This script is meant for MacOS users. Please use the correct script for your operating system"
fi

# Print the help menu to ensure that users know what commands to pass
if [ $# -eq 0 ]; then
  print_help $SCRIPT_NAME
  exit 1
fi

# Check the arguments
while (("$#")); do
  case "$1" in
  "-h" | "--help" | "-?")
    print_help $SCRIPT_NAME
    exit 0
    ;;
  "-c" | "--clone")
    CLONE_CHRONO=1
    CLONE_WA_CHRONO_SIM=1
    shift
    ;;
  "--clone-non-recursive")
    CLONE_CHRONO=0
    shift
    ;;
  "--force-clone")
    CLONE_WA_CHRONO_SIM=1
    FORCE_CLONE_WA_CHRONO_SIM=1
    shift
    ;;
  "-b" | "--build-chrono")
    BUILD_CHRONO=1
    shift
    ;;
  "--anaconda")
    INSTALL_CHRONO_WITH_ANACONDA=1
    shift
    ;;
  "-ci" | "--irrlicht")
    ENABLE_IRRLICHT=1
    shift
    ;;
  "-cp" | "--pychrono")
    ENABLE_PYCHRONO=1
    shift
    ;;
  "-cs" | "--sensor")
    ENABLE_SENSOR=1
    shift
    ;;
  "-csy" | "--synchrono")
    ENABLE_SYNCHRONO=1
    shift
    ;;
  *)
    pretty_print "Unrecognized option: $1\n"
    print_help $SCRIPT_NAME
    exit 1
    ;;
  esac
done

# Homebrew installation
pretty_print "Installing Homebrew."
if ! command -v brew &>/dev/null; then
  ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

  if ! grep -qs "recommended by brew doctor" ~/.zshrc; then
    pretty_print "Put Homebrew location earlier in PATH."
    printf '\n# recommended by brew doctor\n' >>$USER_SHELL_PROFILE
    printf 'export PATH="/usr/local/bin:$PATH"\n' >>$USER_SHELL_PROFILE
    export PATH="/usr/local/bin:$PATH"
  fi
else
  pretty_print "Homebrew is already installed."
fi

# Homebrew OSX libraries
pretty_print "Updating brew formulas"
brew update

pretty_print "Default packages..."
brew install git

TEMP_LS=$(ls)
if [[ "$TEMP_LS" == *"$REPO_NAME"* ]]; then
  cd $REPO_NAME
fi

if [[ $CLONE_WA_CHRONO_SIM ]]; then
  if [[ $FORCE_CLONE_WA_CHRONO_SIM ]]; then
    true
  elif git rev-parse --git-dir >/dev/null 2>&1; then
    if [[ $(basename $(git rev-parse --show-toplevel)) == "$REPO_NAME" ]]; then
      pretty_print "$REPO_NAME is already cloned."

      if git submodule status | egrep -q '^[-]|^[+]'; then
        pretty_print "Initializing the Chrono submodule."
        git submodule update --init
      else
        pretty_print "To force a clone, please flag --force-clone. For help, flag -h."
        exit_error "$REPO_NAME is already cloned. "
      fi
    fi
  fi

  pretty_print "Cloning the $REPO_NAME repo..."

  if [[ $CLONE_CHRONO ]]; then
    git clone --recursive --depth 1 https://github.com/WisconsinAutonomous/wa_chrono_sim.git
  else
    git clone https://github.com/WisconsinAutonomous/wa_chrono_sim.git
  fi

  cd $REPO_NAME
fi

pretty_print "Installing base packages for Chrono build"
brew install cmake eigen libomp

if [[ $BUILD_CHRONO ]]; then
  CHRONO_BASE_DIR=$(git submodule foreach --quiet pwd)
  if [[ ! -d $CHRONO_BASE_DIR ]]; then
    exit_error "$CHRONO_BASE_DIR doesn't exist."
  fi

  cd $CHRONO_BASE_DIR
  mkdir -p build
  cd build

  CMAKE_FLAGS=" -DENABLE_MODULE_VEHICLE:BOOL=ON"

  if [[ $ENABLE_IRRLICHT ]]; then
    CMAKE_FLAGS+=" -DENABLE_MODULE_IRRLICHT:BOOL=ON"

    pretty_print "Installing Irrlicht"
    brew install irrlicht
  fi

  if [[ $ENABLE_PYCHRONO ]]; then
    PYTHON_INCLUDE_DIR=$(python3 -c "from sysconfig import get_paths as gp; print(gp()['include'])")
    PYTHON_EXECUTABLE=$(which python3)
    PYTHON_LIBRARY=$(find $(python3 -c "from sysconfig import get_paths as gp; print(gp()['platstdlib'])") -name "*.dylib")
    CMAKE_FLAGS+=" -DPYTHON_INCLUDE_DIR=$PYTHON_INCLUDE_DIR"
    CMAKE_FLAGS+=" -DPYTHON_EXECUTABLE=$PYTHON_EXECUTABLE"
    CMAKE_FLAGS+=" -DPYTHON_LIBRARY=$PYTHON_LIBRARY"
    CMAKE_FLAGS+=" -DENABLE_MODULE_PYTHON:BOOL=ON"
  fi

  if [[ $ENABLE_SENSOR ]]; then
    exit_error "Cannot enable Chrono::Sensor because a NVIDIA GPU is not available."
  fi

  if [[ $ENABLE_SYNCHRONO ]]; then
    CMAKE_FLAGS+=" -DENABLE_MODULE_IRRLICHT:BOOL=ON"
    exit_error "Cannot enable SynChrono. It is currently not supported"
  fi

  # Ensures compilers are set correctly
  cmake \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DCMAKE_C_COMPILER=$(which clang) \
    -DCMAKE_CXX_COMPILER=$(which clang++) \
    ..

  # Set and build the chrono moduels
  cmake \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DCMAKE_C_COMPILER=$(which clang) \
    -DCMAKE_CXX_COMPILER=$(which clang++) \
    -DENABLE_MODULE_VEHICLE:BOOL=ON \
    $CMAKE_FLAGS \
    .. &&
    make -j$(sysctl hw.physicalcpu | sed 's/hw.physicalcpu: //')
fi

if [[ $INSTALL_CHRONO_WITH_ANACONDA ]]; then
  true
fi
