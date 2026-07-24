from checks.library.storage.helpers import get_drives, get_mount_info, is_network_fs
import logging
import os

DISPLAY_NAME = "Inode Over-usage"
LEVEL = 3

def check():
    drives = get_drives()
    issues = []
    
    for drive in drives:
        try:
            data = get_mount_info(drive)
            if not data:
                return (False, "Could not get mount info!")
            mount_point, fstype = data
            # Skip network drives
            if is_network_fs(fstype):
                continue
                
            if not mount_point:
                continue
                
            stat = os.statvfs(mount_point)
            total_inodes = stat.f_files
            
            # Some filesystems (like NFS) might report 0 inodes
            if total_inodes == 0:
                continue
                
            free_inodes = stat.f_ffree
            used_inodes = total_inodes - free_inodes
            used_percent = (used_inodes / total_inodes) * 100

            if used_percent >= 90:
                issues.append((
                    False, 
                    f"{drive} (mounted at {mount_point}) inodes are {used_percent:.1f}% consumed ({used_inodes:,} used, {free_inodes:,} free). Delete unnecessary small files to free inodes."
                ))
            elif used_percent >= 70:
                issues.append((
                    False, 
                    f"{drive} (mounted at {mount_point}) inodes are {used_percent:.1f}% consumed ({used_inodes:,} used, {free_inodes:,} free). Consider cleaning up old files."
                ))
                
        except Exception as err:
            logging.error(f"Could not check inode usage for {drive}", exc_info=err)
            issues.append((False, f"Could not check inode usage for {drive}: {str(err)}"))
    
    if issues:
        return issues
    return True