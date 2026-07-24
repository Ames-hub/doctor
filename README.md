# Doctor
Doctor for ongoing computer telemetry, observation and recovery

<hr>

"Doctor" is a tool for Debian-based Linux distributions that unifies various health-check tools (such as SMART, lm-sensors, fwupd, etc.) across Linux into one tool. 

# Intention 
The intended product of this tool is improved ability to diagnose issues and issue patches/repairs, and also to provide an early-warning system for any Debian-based Linux distro by letting the user know of any system problems, in a highly configurable manner.

On a side note, I believe this can help many users. I myself, while programming this, discovered that my boot drives SSD lifespan was only at 11% left!

# Installation
Run this command:
```
curl -fsSL https://raw.githubusercontent.com/ames-hub/doctor/main/install.sh | sudo bash
```
If you wish to review what this command does, please see in the project root: `./install.sh`

# Requirements
### Systemd
Doctor is intended as a systemd daemon, however it can be deployed using other systems. However, if other systems are used (such as OpenRC or Runit) I will not guarantee that it will run. This has only been tested as a Systemd service. If it CAN run, it will not run at full quality of performance because it has some systemd only checks.
### Journalctl
Doctor uses Journalctl to discover various bits of system information, and is therefore required. Without this, doctor's quality of performance will be highly degraded.
### Python3.13
This program requires Python3.13.<br>
Otherwise, `setup.sh` should install anything else needed.
### Super-user access
As this system checks things like if the Kernel needs updating, it is required that this program runs as root. Either that, or you can delete the file "./checks/kernel_update.py" (and any others that need super user access)
### Notify-send package
For non-headless computers, (computers with a desktop) notify-send package is required as its what we use to notify users of a problem. 
### dmesg
Required. I'll elaborate on why later

# Note
This was built because I couldn't for the life of me find any tool for linux that would do what this does, and I needed some tool that would tell me if my server was dying. Thus its primarily meant for personal use.