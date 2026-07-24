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
class missing_other_component(Exception):
    def __init__(self, name:str, *args):
        super().__init__(name, *args)
class unavailable_sys_info(Exception):
    """ Called when a component like journalctl returns no data when it should've given data. """
    def __init__(self, *args):
        super().__init__(*args)
class too_verbose(Exception):
    def __init__(self, *args):
        super().__init__(*args)