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
    Returns physical disk devices only.
    Example: ['/dev/sda', '/dev/nvme0n1']
    """

    result = subprocess.run(
        [
            "lsblk",
            "-J",
            "-d",
            "-o", "NAME,TYPE,ROTA"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        return []

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        return []

    return [
        f"/dev/{device['name']}"
        for device in data.get("blockdevices", [])
        if device.get("type") == "disk"
        and not device["name"].startswith("zram")
    ]

def get_mount_info(device):
    """Return mount points and filesystem types for a device and its partitions."""
    try:
        result = subprocess.run(
            [
                "lsblk",
                "-ln",
                "-o", "MOUNTPOINT,FSTYPE",
                device
            ],
            capture_output=True,
            text=True,
            check=True
        )

        mounts = []

        for line in result.stdout.splitlines():
            parts = line.split(maxsplit=1)

            if len(parts) == 2 and parts[0] != "":
                mount_point, fstype = parts
                mounts.append((mount_point, fstype))

        return mounts

    except (OSError, subprocess.CalledProcessError):
        logging.error(f"Couldn't get mount info for {device}", exc_info=True)

    return []

def is_network_fs(fstype):
    """Check if filesystem type is network-based"""
    network_fs = {
        'nfs', 'nfs4', 'smb', 'cifs', 'afs', 'ceph', 
        'glusterfs', 'fuse.sshfs', 'sshfs', 'gvfs'
    }
    return fstype in network_fs