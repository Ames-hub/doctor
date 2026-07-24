from checks.library.storage.helpers import get_drives
import shutil
import os

DISPLAY_NAME = "Disk Space Usage"
LEVEL = 3  # Yellow-flag

def check():
    """Check disk usage for all mounted partitions"""
    drives = get_drives()
    issues = []

    for drive in drives:
        try:
            # Get mount point for this drive
            result = os.popen(f"lsblk -no MOUNTPOINT {drive} 2>/dev/null").read().strip()
            if not result:
                continue  # Skip drives that don't have mount points

            # Use the first mount point found
            mount_point = result.split('\n')[0]

            total, used, free = shutil.disk_usage(mount_point)
            used_percent = (used / total) * 100

            if used_percent >= 95:
                issues.append((False, f"{drive} (mounted at {mount_point}) is {used_percent:.1f}% full ({used // 1024 ** 3}GB used, { free // 1024 ** 3}GB free). Free up space immediately!"))
            elif used_percent >= 80:
                issues.append((False, f"{drive} (mounted at {mount_point}) is {used_percent:.1f}% full ({used // 1024 ** 3}GB used, {free // 1024 ** 3}GB free). Consider clearing storage soon."))
        except Exception as e:
            issues.append((False, f"Could not check disk usage for {drive}: {str(e)}"))

    if issues:
        return issues
    return True