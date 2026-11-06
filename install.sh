```bash
#!/bin/bash
set -e

REPO_URL="github.com/ames-hub/doctor.git"
INSTALL_DIR="/opt/doctor"
SERVICE_NAME="doctor.service"
SYSTEMD_DIR="/etc/systemd/system"

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
OFFLINE=false

for arg in "$@"; do
    case "$arg" in
        --offline)
            OFFLINE=true
            ;;
    esac
done

# Check if the script is ran as root
if [ "$EUID" -ne 0 ]; then
    echo "This installer must be run as root. Try: sudo ./install.sh"
    exit 1
fi

# Detect Linux distribution
echo "Detecting Linux distribution..."

if [ ! -f /etc/os-release ]; then
    echo "Error: Cannot identify Linux distribution."
    exit 1
fi

source /etc/os-release

DISTRO="${ID,,}"
DISTRO_LIKE="${ID_LIKE,,}"

if [[ "$DISTRO" == "fedora" ]]; then
    PACKAGE_MANAGER="dnf"
    SYSTEM_PACKAGES=(
        libnotify
        util-linux
        smartmontools
        git
        rsync
    )

elif [[ "$DISTRO" == "ubuntu" || " $DISTRO_LIKE " == *" ubuntu "* ]]; then
    PACKAGE_MANAGER="apt"
    SYSTEM_PACKAGES=(
        libnotify-bin
        util-linux
        smartmontools
        git
        rsync
    )

else
    echo "Error: Unsupported Linux distribution: $PRETTY_NAME"
    echo "Supported distributions:"
    echo "  - Fedora"
    echo "  - Ubuntu and Ubuntu-based distributions"
    exit 1
fi

echo "Detected: $PRETTY_NAME"
echo "Package manager: $PACKAGE_MANAGER"

# Install system dependencies
echo "Installing system dependencies..."

if [ "$PACKAGE_MANAGER" = "dnf" ]; then
    dnf install -y "${SYSTEM_PACKAGES[@]}"
else
    apt-get update
    apt-get install -y "${SYSTEM_PACKAGES[@]}"
fi

# Check Python version
echo "Checking Python version..."

PYTHON_BIN=""

PYTHON_LOCATIONS=(
    "python3.14"
    "/usr/bin/python3.14"
    "/usr/local/bin/python3.14"
    "/home/linuxbrew/.linuxbrew/bin/python3.14"
)

for python in "${PYTHON_LOCATIONS[@]}"; do
    if command -v "$python" &> /dev/null || [ -x "$python" ]; then
        PYTHON_BIN=$(command -v "$python" 2>/dev/null || echo "$python")
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3.14 is required."
    echo "No compatible Python installation found."
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

if [ "$PYTHON_VERSION" != "3.14" ]; then
    echo "Error: Python 3.14 is required."
    echo "Found Python $PYTHON_VERSION at $PYTHON_BIN"
    exit 1
fi

echo "Found Python 3.14: $PYTHON_BIN"

echo "Checking venv support..."

if ! "$PYTHON_BIN" -m venv --help &> /dev/null; then
    echo "Error: Python 3.14 was found, but it does not have venv support."
    echo "Install Python with the venv module included."
    exit 1
fi

# Clone repository
if [ -f "$INSTALL_DIR/main.py" ]; then
    echo "$INSTALL_DIR already exists."

    if [ "$OFFLINE" = true ]; then
        echo "1) Clean reinstall (delete and copy from local directory)"
        echo "2) Update (copy latest changes from local directory)"
    else
        echo "1) Clean reinstall (delete and re-clone)"
        echo "2) Update (pull latest changes)"
    fi

    read -rp "Choose an option [1/2]: " EXISTING_CHOICE

    case "$EXISTING_CHOICE" in
        1)
            echo "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
            mkdir -p "$INSTALL_DIR"

            if [ "$OFFLINE" = true ]; then
                echo "Copying local repository..."
                rsync -a --exclude='.git' --exclude='install.sh' --exclude='venv' "${SOURCE_DIR}/" "${INSTALL_DIR}/"
            else
                echo "Cloning repository..."
                git clone "https://${REPO_URL}" "$INSTALL_DIR"
            fi
            ;;

        2)
            if [ "$OFFLINE" = true ]; then
                echo "Updating existing installation from local directory..."
                rsync -a --exclude='.git' --exclude='install.sh' --exclude='venv' "${SOURCE_DIR}/" "${INSTALL_DIR}/"
            else
                echo "Updating existing installation..."
                git -C "$INSTALL_DIR" pull
            fi
            ;;

        *)
            echo "Invalid choice. Aborting."
            exit 1
            ;;
    esac
else
    if [ "$OFFLINE" = true ]; then
        echo "Copying local repository..."
        mkdir -p "$INSTALL_DIR"
        rsync -a --exclude='.git' --exclude='install.sh' --exclude='venv' "${SOURCE_DIR}/" "${INSTALL_DIR}/"
    else
        echo "Cloning repository..."
        git clone "https://${REPO_URL}" "$INSTALL_DIR"
    fi
fi

# Create Python virtual environment
echo "Creating Python virtual environment..."

if ! "$PYTHON_BIN" -m venv "${INSTALL_DIR}/venv"; then
    echo "Error: Failed to create Python virtual environment."
    echo "Make sure the venv package for $PYTHON_BIN is installed."
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."

"${INSTALL_DIR}/venv/bin/python" -m pip install --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

# Install doctor command wrapper
echo "Installing 'doctor' command wrapper..."

cat << 'EOF' > /usr/local/bin/doctor
#!/usr/bin/env bash
exec "/opt/doctor/venv/bin/python" /opt/doctor/main.py "$@"
EOF

chmod +x /usr/local/bin/doctor

# Check if systemd is installed
if ! command -v systemctl &> /dev/null; then
    echo ""
    echo "=================================================================="
    echo "We don't support this daemon manager, since we're a systemd"
    echo "program. If you want to install us, you'll have to register this"
    echo "program to runit or whatever you're using yourself. (If its not already registered)"
    echo "=================================================================="
    exit 0
fi

# Move doctor.service to systemd services folder
if [ ! -f "${INSTALL_DIR}/${SERVICE_NAME}" ]; then
    echo "Error: ${INSTALL_DIR}/${SERVICE_NAME} not found. Cannot proceed."
    exit 1
fi

echo "Installing systemd service..."

mv "${INSTALL_DIR}/${SERVICE_NAME}" "${SYSTEMD_DIR}/${SERVICE_NAME}"

systemctl daemon-reload
systemctl enable "$SERVICE_NAME"
systemctl start "$SERVICE_NAME"

echo ""
echo "Doctor installation complete."
echo "Please check status with: systemctl status ${SERVICE_NAME}"
```