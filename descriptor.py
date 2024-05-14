class Descriptor:
    # The Descriptor class represents a file descriptor in a file system.
    def __init__(self, num, file_type, size, name):
        self.id = num  # Unique identifier for the descriptor
        self.name = name  # Name of the file
        self.type = file_type  # Type of the file (e.g., directory, regular file)
        self.nlink = 1  # Number of links to the file
        self.links = [self]  # List of links to the file
        self.size = size  # Size of the file in bytes
        self.blocks = []  # List of blocks that store the file's data

    def show(self):
        print(
            f'id={self.id}, name={self.name}, type={self.type}, nlink={self.nlink}, size={self.size}, nblock={len(self.blocks)}')


class Link:
    # The Link class represents a link to a file in a file system.
    def __init__(self, descriptor, name):
        descriptor.nlink += 1  # Increment the number of links to the file
        self.descriptor = descriptor  # The descriptor of the file being linked to
        self.name = name  # The name of the link

    def show(self):
        print(
            f'id={self.descriptor.id}, name={self.name}->{self.descriptor.name}, type={self.descriptor.type}, nlink={self.descriptor.nlink}, size={self.descriptor.size}, nblock={len(self.descriptor.blocks)}')
