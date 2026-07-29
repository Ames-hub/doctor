import subprocess
import logging
import json

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

def get_life_left(drive: str) -> float | None:
    result = subprocess.run(
        ["smartctl", "-A", "-j", drive],
        capture_output=True,
        text=True
    )

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return None

    # NVMe: unambiguous, reported directly
    nvme_log = data.get("nvme_smart_health_information_log")
    if nvme_log and "percentage_used" in nvme_log:
        return max(0, 100 - nvme_log["percentage_used"])

    attrs = data.get("ata_smart_attributes", {}).get("table", [])
    attrs_by_id = {a["id"]: a for a in attrs}

    # Attributes where the NORMALIZED value IS the percent life remaining
    for attr_id in (202, 231, 233):  # Percent_Lifetime_Remain, SSD_Life_Left, Media_Wearout_Indicator
        if attr_id in attrs_by_id:
            return attrs_by_id[attr_id]["value"]

    # Attributes where the RAW value IS the percent life remaining
    if 169 in attrs_by_id:  # Remaining_Lifetime_Perc
        return attrs_by_id[169]["raw"]["value"]

    # Best-effort estimate from wear/erase data
    ASSUMED_MAX_PE_CYCLES = 3000
    for attr_id in (173, 177):  # These are "Ave_Block-Erase_Count", "Wear_Leveling_Count"
        if attr_id in attrs_by_id:
            erase_count = attrs_by_id[attr_id]["raw"]["value"]
            return round(max(0, 100 - (erase_count / ASSUMED_MAX_PE_CYCLES * 100)), 1)

    return None

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