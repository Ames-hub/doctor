#!/bin/bash
set -e

INSTALL_DIR="/opt/doctor"
SERVICE_NAME="doctor.service"
SYSTEMD_DIR="/etc/systemd/system"

# Check if the script is ran as root
if [ "$EUID" -ne 0 ]; then
    echo "This uninstaller must be run as root. Try: sudo ./uninstall.sh"
    exit 1
fi

systemctl disable "$SERVICE_NAME"
systemctl stop "$SERVICE_NAME"

echo "Removing existing installation..."
rm -rf "$INSTALL_DIR"

echo "Uninstalling 'doctor' command wrapper..."
rm /usr/local/bin/doctor

rm "${SYSTEMD_DIR}/${SERVICE_NAME}"

systemctl daemon-reload

echo ""
echo "Doctor removal complete."