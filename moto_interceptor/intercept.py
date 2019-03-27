import os


class FileLineManager(object):
    file_path = None

    def __init__(self):
        self.entries = []

    def add_entries(self, entries):
        self.entries.extend(entries)

        with open(self.file_path, "a") as f:
           for entry in entries:
                f.write(entry)

    def remove_entries(self):
        with open(self.file_path, "r") as f:
            lines = f.readlines()

        with open(self.file_path, "w") as f:
            for line in lines:
                if line not in self.entries:
                    f.write(line)


class Dnsmasq(FileLineManager):

    file_path = '/usr/local/etc/dnsmasq.conf'


class Hostfile(FileLineManager):
    file_path = '/etc/hosts'


class Resolver(FileLineManager):
    file_path = '/etc/resolver/amazonaws.com'

    def __init__(self):
        os.makedirs('/etc/resolver', exist_ok=True)

        super().__init__()

    def add_entries(self, entries):
        super().add_entries(entries)
        os.utime('/etc/resolver')

    def remove_entries(self):
        super().remove_entries()
        os.utime('/etc/resolver')
