from checks.library.storage.helpers import get_drives
import subprocess
import re
import os

DISPLAY_NAME = "Filesystem Read-Only Remounts"
LEVEL = 2  # Orange-flag

def check():
    """Check if any filesystem has been remounted read-only due to errors"""
    drives = get_drives()
    issues = []
    
    try:
        # Get dmesg output once
        result = subprocess.run(['dmesg'], capture_output=True, text=True)
        dmesg_output = result.stdout
        
        # Check each drive for read-only remount events
        for drive in drives:
            drive_name = os.path.basename(drive)
            
            # Look for patterns indicating read-only remounts for this specific drive
            patterns = [
                rf'{drive_name}.*remounting filesystem read-only',
                rf'{drive_name}.*remount\s+read-only',
                rf'{drive}.*filesystem\s+read-only\s+remount',
                rf'{drive_name}.*mounted\s+read-only',
                rf'{drive}.*read-only'  # Broader pattern for the specific device
            ]
            
            found_issues = []
            for line in dmesg_output.splitlines():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        found_issues.append(line.strip()[:150])
                        break
            
            if found_issues:
                msg = "; ".join(found_issues[:3])
                if len(found_issues) > 3:
                    msg += f" (and {len(found_issues)-3} more events)"
                issues.append((False, f"{drive} was remounted read-only. This indicates severe disk errors. {msg}"))
        
        if issues:
            return issues
        return True
            
    except Exception as e:
        return (False, f"Could not check for read-only remounts: {str(e)}")