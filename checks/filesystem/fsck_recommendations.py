from checks.library.storage.helpers import get_drives
import subprocess
import os
import re

DISPLAY_NAME = "fsck Recommendations"
LEVEL = 1  # Red-flag

def check():
    """Check if filesystems need fsck (filesystem check) on all drives"""
    drives = get_drives()
    issues = []
    
    for drive in drives:
        try:
            drive_name = os.path.basename(drive)
            fsck_needed = []
            
            # Check if it's an ext filesystem and needs fsck
            try:
                # Get filesystem type
                result = subprocess.run(['blkid', '-o', 'value', '-s', 'TYPE', drive], 
                                       capture_output=True, text=True)
                fs_type = result.stdout.strip()
                
                if fs_type.startswith('ext'):
                    # Check mount count and max mount count
                    tune_result = subprocess.run(
                        ['tune2fs', '-l', drive], 
                        capture_output=True, 
                        text=True
                    )
                    
                    if tune_result.returncode == 0:
                        output = tune_result.stdout
                        
                        mount_count = None
                        max_mount_count = None
                        
                        for line in output.splitlines():
                            if 'Mount count' in line:
                                mount_count = int(re.search(r'\d+', line).group())
                            elif 'Maximum mount count' in line:
                                max_mount_count = int(re.search(r'\d+', line).group())
                        
                        # Determine if fsck is needed
                        if mount_count is not None and max_mount_count is not None:
                            if mount_count >= max_mount_count and max_mount_count > 0:
                                fsck_needed.append(
                                    f"mount count reached ({mount_count}/{max_mount_count})"
                                )
                        
                        # Check filesystem state
                        lowered_output = output.lower()
                        if 'filesystem state:' in lowered_output and 'not clean' in lowered_output:
                            fsck_needed.append("filesystem has dirty bit set")

                elif fs_type == 'btrfs':
                    # Check BTRFS for errors
                    btrfs_result = subprocess.run(
                        ['btrfs', 'device', 'stats', drive],
                        capture_output=True,
                        text=True
                    )
                    if btrfs_result.returncode == 0:
                        if 'write_io_errs' in btrfs_result.stdout and '0' not in btrfs_result.stdout:
                            fsck_needed.append("BTRFS reported I/O errors, run btrfs check")

                elif fs_type == 'xfs':
                    # Check XFS for issues
                    xfs_result = subprocess.run(
                        ['xfs_repair', '-n', drive],
                        capture_output=True,
                        text=True
                    )
                    if 'corruption' in xfs_result.stdout.lower():
                        fsck_needed.append("XFS corruption detected, run xfs_repair")

            except Exception as e:
                # Skip if commands fail (not ext filesystem or permission)
                pass

            # Check if there's a force fsck file for this drive
            forcefsck_path = f'/forcefsck.{drive_name}'
            if os.path.exists(forcefsck_path) or os.path.exists('/forcefsck'):
                fsck_needed.append("forced fsck requested on next boot")

            if fsck_needed:
                message = "; ".join(fsck_needed[:3])
                if len(fsck_needed) > 3:
                    message += f" (and {len(fsck_needed)-3} more issues)"
                issues.append((False, f"Filesystem check required for {drive}. {message}"))

        except Exception as e:
            issues.append((False, f"Could not check {drive} for fsck recommendations: {str(e)}"))

    if issues:
        return issues
    return True