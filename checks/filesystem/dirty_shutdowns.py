from checks.library.storage.helpers import get_drives
import subprocess
import re
import os

DISPLAY_NAME = "Dirty Shutdowns Detection"
LEVEL = 2  # Orange-flag

def check():
    drives = get_drives()
    issues = []
    
    try:
        result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=10)
        dmesg_output = result.stdout
        
        # Build one combined regex for better performance
        patterns = [
            r'recover(?:ing|y).*?{drive}',
            r'journal\s+recovery.*?{drive}',
            r'fsck\s+recovery.*?{drive}',
            r'unclean\s+shutdown.*?{drive}',
            r'force\s+fsck.*?{drive}',
            r'{drive}.*?not clean',
            r'{drive}.*?dirty'
        ]
        
        for drive in drives:
            drive_name = os.path.basename(drive)
            
            # Skip network devices (add this to all checks!)
            if ':' in drive or drive.startswith('//'):
                continue
            
            # Compile pattern for this drive
            combined_pattern = '|'.join(p.replace('{drive}', re.escape(drive_name)) for p in patterns)
            matches = re.findall(combined_pattern, dmesg_output, re.IGNORECASE)
            
            if matches:
                issues.append((False, f"Unclean shutdown detected on {drive}: {matches[0][:100]}"))
    except Exception as e:
        return (False, f"Could not check for dirty shutdowns: {str(e)}")

    if issues:
        return issues

    return True