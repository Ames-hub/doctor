import subprocess

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
    """Reusable helper for all storage checks"""
    try:
        with open('/proc/mounts', 'r') as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[0] == device:
                    return parts[1]  # mount point
    except:
        pass
    return None

def is_network_fs(fstype):
    """Check if filesystem type is network-based"""
    network_fs = {
        'nfs', 'nfs4', 'smb', 'cifs', 'afs', 'ceph', 
        'glusterfs', 'fuse.sshfs', 'sshfs', 'gvfs'
    }
    return fstype in network_fs