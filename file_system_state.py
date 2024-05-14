class FileSystemState:
    file_system = None
    block_size = 128
    max_length = 14

    @staticmethod
    def is_initialised():
        if FileSystemState.file_system is None:
            print('The file system is not initialised')
            return 1
        return 0
