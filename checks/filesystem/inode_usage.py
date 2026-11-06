from checks.library.storage.helpers import get_drives, get_mount_info, is_network_fs
import logging
import os

DISPLAY_NAME = "Inode Over-usage"
LEVEL = 3

def check():
    drives = get_drives()
    issues = []

    for drive in drives:
        mounts = get_mount_info(drive)

        if not mounts:
            continue

        for mount_point, fstype in mounts:

            if not mount_point or not os.path.isdir(mount_point):
                continue

            if is_network_fs(fstype):
                continue

            try:
                stat = os.statvfs(mount_point)

                total_inodes = stat.f_files

                if total_inodes == 0:
                    continue

                free_inodes = stat.f_ffree
                used_inodes = total_inodes - free_inodes
                used_percent = (used_inodes / total_inodes) * 100

                if used_percent >= 90:
                    issues.append((
                        False,
                        f"{drive} (mounted at {mount_point}) inodes are "
                        f"{used_percent:.1f}% consumed "
                        f"({used_inodes:,} used, {free_inodes:,} free). "
                        "Delete unnecessary small files to free inodes."
                    ))

                elif used_percent >= 70:
                    issues.append((
                        False,
                        f"{drive} (mounted at {mount_point}) inodes are "
                        f"{used_percent:.1f}% consumed "
                        f"({used_inodes:,} used, {free_inodes:,} free). "
                        "Consider cleaning up old files."
                    ))

            except (OSError, PermissionError) as e:
                logging.warning(
                    "Could not check inode usage for %s: %s",
                    mount_point, e
                )

    if issues:
        return issues

    return True