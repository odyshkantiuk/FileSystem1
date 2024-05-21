class FileSystemState:
    file_system = None
    cwd = None
    block_size = 128
    max_length = 14

    @staticmethod
    def is_initialised():
        if FileSystemState.file_system is None:
            print('The file system is not initialised')
            return 1
        return 0

    @staticmethod
    def register_descriptor(descriptor):
        FileSystemState.file_system.descriptors.append(descriptor)
        FileSystemState.file_system.descriptors_num += 1

    @staticmethod
    def check_path_exist(pathname: str, is_last_file: bool = False):
        if pathname == "":
            return FileSystemState.cwd
        if pathname == '/':
            return FileSystemState.file_system.root
        path_array = pathname.split('/')
        if pathname.startswith('/'):
            local_cwd = FileSystemState.file_system.root
            path_array.pop(0)
        else:
            local_cwd = FileSystemState.cwd
        new_local_cwd = local_cwd
        symlink_counter = 0
        if is_last_file:
            j = 0
            while j < len(path_array):
                if symlink_counter > 20:
                    print(f'Too many symlinks symlink {symlink_counter} > 20')
                    return None
                path_part = path_array[j]
                if path_part == '.':
                    j += 1
                    continue
                if path_part == '..':
                    new_local_cwd = local_cwd.parent
                    local_cwd = new_local_cwd
                    j += 1
                    continue
                array_size = len(path_array)
                for i in range(len(local_cwd.child_directories)):
                    if path_part == local_cwd.child_directories[i].name:
                        if local_cwd.child_directories[i].descriptor.type == 'symlink':
                            symlink_counter += 1
                            sym_path = local_cwd.child_directories[i].content
                            sym_path_array = sym_path.split('/')
                            if sym_path.startswith('/'):
                                new_local_cwd = FileSystemState.file_system.root
                                sym_path_array.pop(0)
                            for ind, symm in enumerate(sym_path_array):
                                path_array.insert(j + ind + 1, symm)
                            break
                        elif j == len(path_array) - 1 and local_cwd.child_directories[i].descriptor.TYPE == 'regular':
                            return new_local_cwd, local_cwd.child_directories[i].descriptor
                        elif j == len(path_array) - 1:
                            return None, None
                        else:
                            new_local_cwd = local_cwd.child_directories[i]
                            break
                if new_local_cwd == local_cwd and array_size == len(path_array):
                    return None, None
                local_cwd = new_local_cwd
                j += 1
            return new_local_cwd
        else:
            j = 0
            while j < len(path_array):
                if symlink_counter > 20:
                    print(f'Too many symlinks symlink {symlink_counter} > 20')
                    return None
                path_part = path_array[j]
                if path_part == '.':
                    j += 1
                    continue
                if path_part == '..':
                    new_local_cwd = local_cwd.parent
                    local_cwd = new_local_cwd
                    j += 1
                    continue
                array_size = len(path_array)
                for i in range(len(local_cwd.child_directories)):
                    if path_part == local_cwd.child_directories[i].name:
                        if local_cwd.child_directories[i].descriptor.type == 'symlink':
                            symlink_counter += 1
                            sym_path = local_cwd.child_directories[i].content
                            sym_path_array = sym_path.split('/')
                            if sym_path.startswith('/'):
                                new_local_cwd = FileSystemState.file_system.root
                                sym_path_array.pop(0)
                            for ind, symm in enumerate(sym_path_array):
                                path_array.insert(j + ind + 1, symm)
                            break
                        else:
                            new_local_cwd = local_cwd.child_directories[i]
                            break
                if new_local_cwd == local_cwd and array_size == len(path_array):
                    return None
                local_cwd = new_local_cwd
                j += 1
            return new_local_cwd
