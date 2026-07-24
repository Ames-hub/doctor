import subprocess
import logging

def is_hdd(drive):
    """Check if a drive is an HDD (not SSD or NVMe)"""
    try:
        result = subprocess.run(
            ["smartctl", "-i", drive],
            capture_output=True,
            text=True
        )
        
        output = result.stdout.lower()
        
        # Skip if it's clearly an SSD or NVMe
        if "solid state" in output or "nvme" in output or "non-volatile" in output:
            return False
        
        # Check for rotation rate - HDDs have this, SSDs/NVMe don't
        for line in result.stdout.splitlines():
            if "Rotation Rate" in line:
                # If it has a rotation rate and isn't SSD, it's an HDD
                return "solid state" not in line.lower() and "ssd" not in line.lower()
        
        # If no rotation rate info, check device model for SSD/NVMe indicators
        for line in result.stdout.splitlines():
            if "Device Model" in line or "Model Number" in line:
                model = line.lower()
                if "ssd" in model or "nvme" in model:
                    return False
        
        # Default to True if we can't determine it's SSD/NVMe
        return True
        
    except Exception:
        # If we can't determine, assume it might be an HDD and check it
        return True

def get_drives():
    """
    Returns a list of physical drives, e.g:
    ['/dev/sda', '/dev/sdb', '/dev/nvme0n1']
    """

    result = subprocess.run(
        [
            "lsblk",
            "-dn",
            "-o",
            "NAME,TYPE"
        ],
        capture_output=True,
        text=True
    )

    drives = []

    for line in result.stdout.splitlines():
        name, drive_type = line.split()

        if drive_type == "disk":
            drives.append(f"/dev/{name}")

    return drives

def get_mount_info(device):
    """Return mount point and filesystem type for a device or its partitions."""
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                parts = line.split()

                if len(parts) >= 3:
                    mounted_device = parts[0]

                    if mounted_device == device or mounted_device.startswith(device):
                        return parts[1], parts[2]

    except OSError:
        logging.error("Couldn't open /proc/mounts", exc_info=True)

    return None

def is_network_fs(fstype):
    """Check if filesystem type is network-based"""
    network_fs = {
        'nfs', 'nfs4', 'smb', 'cifs', 'afs', 'ceph', 
        'glusterfs', 'fuse.sshfs', 'sshfs', 'gvfs'
    }
    return fstype in network_fs