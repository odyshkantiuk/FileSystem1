class Descriptor:
    # The Descriptor class represents a file descriptor in a file system.
    def __init__(self, num, file_type, size, name, content=None):
        self.id = num  # Unique identifier for the descriptor
        self.name = name  # Name of the file
        self.type = file_type  # Type of the file (e.g., directory, regular file)
        self.nlink = 1  # Number of links to the file
        self.links = [self]  # List of links to the file
        self.size = size  # Size of the file in bytes
        self.blocks = []  # List of blocks that store the file's data
        if file_type == 'symlink':
            self.content = content  # Content of the symbolic link

    def show(self):
        print(
            f'id={self.id}, name={f"{self.name}->{self.content}" if self.type == "symlink" else self.name}, type={self.type}, nlink={self.nlink}, size={self.size}, nblock={len(self.blocks)}, symlink to {self.content}' if self.type == 'symlink' else '')


class Link:
    # The Link class represents a link to a file in a file system.
    def __init__(self, descriptor, name):
        descriptor.nlink += 1  # Increment the number of links to the file
        self.descriptor = descriptor  # The descriptor of the file being linked to
        self.name = name  # The name of the link

    def show(self):
        print(
            f'id={self.descriptor.id}, name={self.name}->{self.descriptor.name}, type={self.descriptor.type}, nlink={self.descriptor.nlink}, size={self.descriptor.size}, nblock={len(self.descriptor.blocks)}')


class Symlink:
    # The Symlink class represents a symbolic link in a file system.
    def __init__(self, name: str, descriptor: Descriptor, parent, content):
        self.name = name  # Name of the symbolic link
        self.descriptor = descriptor  # Descriptor of the symbolic link
        self.parent = parent   # Parent directory of the symbolic link
        self.content = content  # Content of the symbolic link


class Dir:
    # The Dir class represents a directory in a file system.
    def __init__(self, name: str, descriptor: Descriptor, parent):
        self.name = name  # Name of the directory
        if parent is None:  # If the directory is the root directory of the file system (i.e., has no parent)
            self.parent = self  # Set the parent directory to itself
        else:
            self.parent = parent  # Parent directory of the directory
        self.descriptor = descriptor  # Descriptor of the directory
        self.child_descriptors = []  # List of child descriptors
        self.child_directories = []  # List of child directories
        if parent is None:  # If the directory is the root directory of the file system (i.e., has no parent)
            parent_link = Link(descriptor, '..')    # Create a link to itself
        else:
            parent_link = Link(parent.descriptor, '..')  # Create a link to the parent directory
        self.child_descriptors.append(parent_link)  # Add the link to the list of child descriptors
        self.child_descriptors.append(Link(descriptor, '.'))  # Add a link to itself to the list of child descriptors
