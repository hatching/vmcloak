class Machinery(object):
    """Base class that is used by dependencies to manage VM-related
    properties"""
    def __init__(self, name):
        self.name = name

    def attach_iso(self, iso_path):
        """Mount an ISO."""
        raise NotImplementedError

    def detach_iso(self):
        """Detach the ISO file."""
        raise NotImplementedError
