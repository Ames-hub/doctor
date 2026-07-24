import subprocess

def is_virtual_machine() -> bool:
    """
    Detect whether the program is running inside a virtual machine.
    """

    try:
        result = subprocess.run(
            ["systemd-detect-virt"],
            capture_output=True,
            text=True,
            timeout=2
        )

        virt = result.stdout.strip()

        if virt and virt != "none":
            return True

    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    dmi_paths = [
        "/sys/class/dmi/id/product_name",
        "/sys/class/dmi/id/sys_vendor",
        "/sys/class/dmi/id/board_vendor",
    ]

    vm_keywords = [
        "kvm",
        "qemu",
        "virtual",
        "vmware",
        "virtualbox",
        "xen",
        "hyper-v",
        "bhyve",
        "parallels",
    ]

    for path in dmi_paths:
        try:
            with open(path, "r") as f:
                value = f.read().lower()

            if any(keyword in value for keyword in vm_keywords):
                return True

        except FileNotFoundError:
            pass

    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read().lower()

        if "hypervisor" in cpuinfo:
            return True

    except FileNotFoundError:
        pass

    return False