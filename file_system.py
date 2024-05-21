from descriptor import Descriptor, Dir
from file_system_state import FileSystemState


class FileSystem:
    # The FileSystem class represents a file system.
    def __init__(self, descriptors_number):
        root_descriptor = Descriptor(0, 'directory', 0, '/')  # Root descriptor
        root_descriptor.nlink -= 1  # Root directory is not a file, so it does not have a link to itself
        root_directory = Dir('/', root_descriptor, None)  # Root directory
        FileSystemState.cwd = root_directory  # Current working directory
        self.opened_files = []  # List of files that are currently opened in the file system
        self.opened_files_num_descriptors = []  # List of descriptors numbers for the opened files
        self.descriptors_max_num = descriptors_number  # Maximum number of descriptors that can be created in the file system
        self.descriptors_num = 0  # Current number of descriptors in the file system
        self.descriptors = []  # List of all descriptors in the file system
        self.descriptors_bitmap = [0 for i in range(descriptors_number)]  # Bitmap to keep track of which descriptors are in use
        self.blocks = {}  # Dictionary to store the blocks of data in the file system
        self.descriptors.append(root_descriptor)   # Add the root descriptor to the list of descriptors
        self.descriptors_num += 1  # Increment the number of descriptors in the file system
        self.descriptors_bitmap[0] = 1  # Mark the root descriptor as in use
        self.root = root_directory  # Root directory
