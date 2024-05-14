class FileSystem:
    # The FileSystem class represents a file system.
    def __init__(self, descriptors_number):
        self.opened_files = []  # List of files that are currently opened in the file system
        self.opened_files_num_descriptors = []  # List of descriptors numbers for the opened files
        self.descriptors_max_num = descriptors_number  # Maximum number of descriptors that can be created in the file system
        self.descriptors_num = 0  # Current number of descriptors in the file system
        self.descriptors = []  # List of all descriptors in the file system
        self.descriptors_bitmap = [0 for _ in range(descriptors_number)]  # Bitmap to keep track of which descriptors are in use
        self.blocks = {}  # Dictionary to store the blocks of data in the file system
