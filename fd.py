from file_system_state import FileSystemState
from descriptor import Link


class Fd:
    # The fd class represents a file descriptor in a file system.
    def __init__(self, descriptor):
        if isinstance(descriptor, Link):
            self.descriptor = descriptor.descriptor
        else:
            self.descriptor = descriptor
        num = 0
        while num in FileSystemState.file_system.opened_files_num_descriptors:
            num += 1
        FileSystemState.file_system.opened_files_num_descriptors.append(num)
        self.num_descriptor = num
        self.offset = 0
