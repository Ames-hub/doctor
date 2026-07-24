#!/bin/bash
set -e

REPO_URL="github.com/ames-hub/doctor.git"
INSTALL_DIR="/opt/doctor"
SERVICE_NAME="doctor.service"
SYSTEMD_DIR="/etc/systemd/system"

# Check if the script is ran as root
if [ "$EUID" -ne 0 ]; then
    echo "This installer must be run as root. Try: sudo ./install.sh"
    exit 1
fi

# Check Python version
echo "Checking Python version..."

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
PYTHON_MAJOR=$(echo "$PYTHON_VERSION" | cut -d. -f1)
PYTHON_MINOR=$(echo "$PYTHON_VERSION" | cut -d. -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || { [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 13 ]; }; then
    echo "Error: Python 3.13 or newer is required."
    echo "Installed version: Python $PYTHON_VERSION"
    exit 1
fi

echo "Python $PYTHON_VERSION detected. Sufficient."

# Install notify-send, dmesg and smartctl
echo "Installing dependencies..."
apt update
apt install -y libnotify-bin util-linux smartmontools git

# Clone the repository to /opt/doctor (handle existing install)
if [ -d "$INSTALL_DIR" ]; then
    echo "$INSTALL_DIR already exists."
    echo "1) Clean reinstall (delete and re-clone)"
    echo "2) Update (pull latest changes)"
    read -rp "Choose an option [1/2]: " EXISTING_CHOICE

    case "$EXISTING_CHOICE" in
        1)
            echo "Removing existing installation..."
            rm -rf "$INSTALL_DIR"
            echo "Cloning repository..."
            git clone "https://${REPO_URL}" "$INSTALL_DIR"
            ;;
        2)
            echo "Updating existing installation..."
            git -C "$INSTALL_DIR" pull
            ;;
        *)
            echo "Invalid choice. Aborting."
            exit 1
            ;;
    esac
else
    echo "Cloning repository..."
    git clone "https://${REPO_URL}" "$INSTALL_DIR"
fi

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

# Move doctor.service to the systemd services folder
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