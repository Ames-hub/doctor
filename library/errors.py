class missing_systemd(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class missing_journalctl(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class missing_systemctl(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class missing_notifysend(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class missing_dmesg(Exception):
    def __init__(self, *args):
        super().__init__(*args)