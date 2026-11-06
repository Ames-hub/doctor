# Doctor
Doctor for ongoing computer telemetry, observation and recovery

<hr>

"Doctor" is a tool for Debian-based and Fedora-based Linux distributions that unifies various health-check tools (such as SMART, lm-sensors, fwupd, etc.) across Linux into one tool. 

# Intention 
The intended product of this tool is improved ability to diagnose issues, and also to provide an early-warning system for any Debian-based or Fedora/Red-hat Linux distro by letting the user know of any system problems, in a highly configurable manner. It is not meant to fix the problems, it is meant to tell you what's wrong so you can fix it.

On a side note, I believe this can help many users. I myself, while programming this, discovered that my boot drives SSD lifespan was only at 11% left with its smart self-test failing! But programs like Cockpit did not warn me of this.

# Installation
Run this command as root:
```
curl -fsSL https://raw.githubusercontent.com/ames-hub/doctor/main/install.sh | sudo bash
```
If you wish to review what this command does, please see in the project root: `./install.sh`

## Offline install
While this isn't truly offline, it does stop it from trying to clone the repository from github.
This allows you to clone the repo, and simply install it from the already cloned repository.

To do this, clone the repository, then run these commands in folder you downloaded it to.
```
sudo chmod +x ./install.sh
sudo ./install.sh --offline
```

## Uninstallation
Simply go to the project root directory and run the `uninstall.sh` file as root.

# Commands
To run a scan manually instead of once every 12 hours, you can run:
`doctor --scannow`
Anywhere in the terminal

# Requirements
### Systemd
Doctor is intended as a systemd daemon, however it can be deployed using other systems. However, if other systems are used (such as OpenRC or Runit) I will not guarantee that it will run. This has only been tested as a Systemd service. If it CAN run, it will not run at full quality of performance because it has some systemd only checks.
### Journalctl
Doctor uses Journalctl to discover various bits of system information, and is therefore required. Without this, doctor's quality of performance will be highly degraded. Comes standard with Systemd so you should be fine for this.
### Python3.14
This program requires Python3.14.<br>
Otherwise, `setup.sh` should install anything else needed.
### Super-user access
As this system checks things like if the Kernel needs updating, it is required that this program runs as root. Either that, or you can delete the file "./checks/kernel_update.py" (and any others that need super user access)

You can mostly ignore this, as all it should do is write a warning to logs and move on.
### Notify-send package
For attended computers, (computers with a desktop environment, regularly logged into by users without SSH) notify-send package is required as its what we use to notify users of a problem.
### dmesg
Required. I'll elaborate on why later

# Note
This was built because I couldn't for the life of me find any tool for linux that would do what this does, and I needed some tool that would tell me if my server was dying. Thus its primarily meant for personal use.

# Contribution
Contribution to this project is widely welcomed!