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

PYTHON_BIN=""

for version in 3.13 3.14 3.15; do
    if command -v python$version &> /dev/null; then
        PYTHON_BIN=$(command -v python$version)
        break
    fi
done

if [ -z "$PYTHON_BIN" ]; then
    echo "Error: Python 3.13 or newer is required."
    echo "No compatible Python installation found."
    exit 1
fi

PYTHON_VERSION=$("$PYTHON_BIN" -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')

echo "Found new enough Python: $PYTHON_BIN (Python $PYTHON_VERSION)"

# Install dependencies
echo "Installing dependencies..."

apt update
apt install -y libnotify-bin util-linux smartmontools git python3.13-venv

# Clone repository
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

# Create Python virtual environment
echo "Creating Python virtual environment..."

"$PYTHON_BIN" -m venv "${INSTALL_DIR}/venv"

echo "Installing Python dependencies..."

"${INSTALL_DIR}/venv/bin/pip" install --upgrade pip
"${INSTALL_DIR}/venv/bin/pip" install -r "${INSTALL_DIR}/requirements.txt"

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