from checks.library.storage.helpers import get_drives
from library import errors
import subprocess
import shutil
import os

DISPLAY_NAME = "Filesystem Corruption"
LEVEL = 1

def check():
    """Check for filesystem corruption on all drives"""
    drives = get_drives()
    issues = []

    if shutil.which("dmesg") is None:
        raise errors.missing_dmesg
    if shutil.which("journalctl") is None:
        raise errors.missing_journalctl

    corruption_keywords = [
        'corruption',
        'corrupted',
        'filesystem error',
        'ext4_error',
        'EXT4-fs error',
        'fsck',
        'bad block',
        'io error',
        'I/O error',
        'metadata corruption'
    ]

    try:
        # Get logs once
        log_outputs = {}
        try:
            result = subprocess.run(['dmesg'], capture_output=True, text=True)
            log_outputs['dmesg'] = result.stdout
        except:
            pass

        try:
            result = subprocess.run(['journalctl', '-n', '500'], capture_output=True, text=True)
            log_outputs['journalctl'] = result.stdout
        except:
            pass

        # Check each drive for corruption
        for drive in drives:
            drive_name = os.path.basename(drive)
            drive_corruption = []

            for source, output in log_outputs.items():
                for line in output.splitlines():
                    line_lower = line.lower()
                    if drive_name in line_lower or drive in line_lower:
                        for keyword in corruption_keywords:
                            if keyword in line_lower:
                                # Avoid false positives from the check itself
                                if 'corruption check' in line_lower:
                                    continue
                                drive_corruption.append(f"{source}: {line.strip()[:150]}")
                                break

            if drive_corruption:
                msg = "; ".join(drive_corruption[:3])
                if len(drive_corruption) > 3:
                    msg += f" (and {len(drive_corruption)-3} more events)"
                issues.append((False, f"Filesystem corruption detected on {drive}! Immediate action required. {msg}"))

        if issues:
            return issues
        return True

    except Exception as e:
        return (False, f"Could not check for filesystem corruption: {str(e)}")