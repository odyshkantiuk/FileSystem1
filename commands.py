from file_system_state import FileSystemState
from descriptor import Descriptor, Link, Symlink, Dir
from fd import Fd
from file_system import FileSystem

from prettytable import PrettyTable


# Function to initialize the file system with a given number of descriptors
def mkfs(n):
    if FileSystemState.file_system is not None:
        print('The file system has already been initialized')
        return
    FileSystemState.file_system = FileSystem(n)
    print('File system is initialised')


# Function to display the details of a file with a given name
def stat(name):
    if FileSystemState.is_initialised():
        return
    old_path = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and old_path == '':
        old_path = '/'
    desc_name = name.split('/')[-1]
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f"There is no directory with the path {old_path}")
        return
    for descriptor in working_dir.child_descriptors:
        if descriptor.name == desc_name:
            descriptor.show()
            return
    print(f'The file with the name "{name}" does not exist')


# Function to list all the files in the file system
def ls(pathname=''):
    if FileSystemState.is_initialised():
        return
    table = PrettyTable()
    table.field_names = ["id", "name", "type", "nlink", "size", "nblock"]
    if pathname == '':
        for descriptor in FileSystemState.cwd.child_descriptors:
            if isinstance(descriptor, Descriptor):
                table.add_row([descriptor.id, f"{descriptor.name}->{descriptor.content}" if descriptor.type == "symlink" else descriptor.name, descriptor.type, descriptor.nlink, descriptor.size,
                               len(descriptor.blocks)])
            else:
                table.add_row([descriptor.descriptor.id, descriptor.name + '->' + descriptor.descriptor.name,
                               descriptor.descriptor.type, descriptor.descriptor.nlink, descriptor.descriptor.size,
                               len(descriptor.descriptor.blocks)])
        print(table)
        return
    if pathname == '/':
        for descriptor in FileSystemState.file_system.root:
            if isinstance(descriptor, Descriptor):
                table.add_row([descriptor.id, f"{descriptor.name}->{descriptor.content}" if descriptor.type == "symlink" else descriptor.name, descriptor.type, descriptor.nlink, descriptor.size,
                               len(descriptor.blocks)])
            else:
                table.add_row([descriptor.descriptor.id, descriptor.name + '->' + descriptor.descriptor.name,
                               descriptor.descriptor.type, descriptor.descriptor.nlink, descriptor.descriptor.size,
                               len(descriptor.descriptor.blocks)])
        print(table)
        return
    working_dir = FileSystemState.check_path_exist(pathname)
    if working_dir is None:
        print(f'There is no directory with the path {pathname}')
        return
    for descriptor in working_dir.child_descriptors:
        if isinstance(descriptor, Descriptor):
            table.add_row([descriptor.id, f"{descriptor.name}->{descriptor.content}" if descriptor.type == "symlink" else descriptor.name, descriptor.type, descriptor.nlink, descriptor.size,
                           len(descriptor.blocks)])
        else:
            table.add_row([descriptor.descriptor.id, descriptor.name + '->' + descriptor.descriptor.name,
                           descriptor.descriptor.type, descriptor.descriptor.nlink, descriptor.descriptor.size,
                           len(descriptor.descriptor.blocks)])
    print(table)


# Function to create a file with a given name
def create(name):
    if FileSystemState.is_initialised():
        return
    old_path = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and old_path == '':
        old_path = '/'
    desc_name = name.split('/')[-1]
    if len(str(desc_name)) > FileSystemState.max_length:
        print(
            f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
    if FileSystemState.file_system.descriptors_num >= FileSystemState.file_system.descriptors_max_num:
        print('All descriptors are used')
        return
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f'There is no directory with the path {old_path}')
        return
    for descriptor in working_dir.child_descriptors:
        if descriptor.name == name:
            print(f'The file with the name "{name}" already exists')
            return
    # Find an unused descriptor
    descriptor_num = None
    for i, value in enumerate(FileSystemState.file_system.descriptors_bitmap):
        if not value:
            FileSystemState.file_system.descriptors_bitmap[i] = 1
            descriptor_num = i
            break
    # Create a new descriptor for the file
    descriptor = Descriptor(descriptor_num, 'regular', 0, desc_name)
    FileSystemState.register_descriptor(descriptor)
    working_dir.child_descriptors.append(descriptor)


# Function to open a file with a given name
def open_file(name):
    if FileSystemState.is_initialised():
        return
    oldPath = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and oldPath == '':
        oldPath = '/'
    descName = name.split('/')[-1]
    workingDir = FileSystemState.check_path_exist(oldPath)
    if workingDir is None:
        print(f'There is no directory with the path {oldPath}')
        return
    for descriptor in workingDir.child_descriptors:
        if descriptor.name == descName:
            if isinstance(descriptor, Descriptor) and descriptor.type == 'symlink':
                print('We can\'t open symlink as file')
                return
            opened_file = Fd(descriptor)
            FileSystemState.file_system.opened_files.append(opened_file)
            print(f'fd = {opened_file.num_descriptor}')
            return
    print(f'The file with the name "{name}" does not exist')


# Function to close a file
def close(fd):
    if FileSystemState.is_initialised():
        return
    if fd in FileSystemState.file_system.opened_files_num_descriptors:
        FileSystemState.file_system.opened_files_num_descriptors.remove(fd)
        for openedFile in FileSystemState.file_system.opened_files:
            if openedFile.num_descriptor == fd:
                FileSystemState.file_system.opened_files.remove(openedFile)
                del openedFile
                return
    print(f'There is no opened file with the id "{fd}"')


# Function to move the file pointer to a specific offset
def seek(fd, offset):
    if FileSystemState.is_initialised():
        return
    if fd not in FileSystemState.file_system.opened_files_num_descriptors:
        print(f'There is no opened file with the id "{fd}"')
        return
    for openedFile in FileSystemState.file_system.opened_files:
        if openedFile.num_descriptor == fd:
            openedFile.offset = offset
            return


# Function to read a specific size from a file
def read(fd, size):
    if FileSystemState.is_initialised():
        return
    if fd not in FileSystemState.file_system.opened_files_num_descriptors:
        print(f'There is no opened file with the id "{fd}"')
        return
    for opened_file in FileSystemState.file_system.opened_files:
        if opened_file.num_descriptor == fd:
            if opened_file.descriptor.size < opened_file.offset + size:
                print(f'Unable to read size too large {opened_file.offset + size}')
                return
            num = opened_file.offset // FileSystemState.block_size
            answer = ""
            # Iterate over the range from the current offset to the offset plus the requested size
            for i in range(opened_file.offset, opened_file.offset + size):
                # If the current byte is the last byte of the current block increment the block number
                if i == FileSystemState.block_size * num + FileSystemState.block_size:
                    num += 1
                # Add the byte at the current position to the answer
                answer += str(opened_file.descriptor.blocks[num][i - num * FileSystemState.block_size])
            print(answer)


# Function to write a bytes to a file
def write(fd, size, val):
    if FileSystemState.is_initialised():
        return
    if len(str(val)) != 1:
        print('Value should be 1 byte size')
        return
    if fd not in FileSystemState.file_system.opened_files_num_descriptors:
        print(f'There is no opened file with the id "{fd}"')
        return
    for opened_file in FileSystemState.file_system.opened_files:
        if opened_file.num_descriptor == fd:
            num = len(opened_file.descriptor.blocks)
            # While the total size of the blocks is greater than the new size plus one block size add a new block to the file
            while opened_file.offset + size > num * FileSystemState.block_size:
                opened_file.descriptor.blocks.append(['\0' for _ in range(FileSystemState.block_size)])
                num += 1
            num = 0
            # Iterate over the range from the current offset to the offset plus the size
            for i in range(opened_file.offset + size):
                # If the current byte is the last byte of the current block increment the block number
                if i == FileSystemState.block_size * num + FileSystemState.block_size:
                    num += 1
                # Write the byte at the current position in the file
                if i >= opened_file.offset:
                    opened_file.descriptor.blocks[num][i - num * FileSystemState.block_size] = val
            # If the file size is smaller than the current offset plus the size update the file size
            if opened_file.descriptor.size < opened_file.offset + size:
                opened_file.descriptor.size = opened_file.offset + size
            return


# Function to create a link to a file
def link(name1, name2):
    if FileSystemState.is_initialised():
        return
    filePath = "/".join(name1.split('/')[:-1])
    if len(name1.split('/')) == 2 and filePath == '':
        filePath = '/'
    desc_file_name = name1.split('/')[-1]
    working_file_dir = FileSystemState.check_path_exist(filePath)
    if working_file_dir is None:
        print(f'There is no directory with the path {filePath}')
        return
    link_path = "/".join(name2.split('/')[:-1])
    if len(name2.split('/')) == 2 and link_path == '':
        link_path = '/'
    desc_link_name = name2.split('/')[-1]
    working_link_dir = FileSystemState.check_path_exist(link_path)
    if working_link_dir is None:
        print(f'There is no directory with the path {link_path}')
        return
    if len(str(desc_link_name)) > FileSystemState.max_length:
        print(
            f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
    for descriptor in working_link_dir.child_descriptors:
        if descriptor.name == desc_link_name:
            print(f'The file with the name "{name2}" already exists')
            return
    for descriptor in working_file_dir.child_descriptors:
        if descriptor.name == desc_file_name:
            if isinstance(descriptor, Descriptor) and descriptor.type == 'symlink':
                print('We can\'t do link to symlink file')
                return
            if isinstance(descriptor, Link):
                print('You can\'t create link to link')
                return
            new_link = Link(descriptor, desc_link_name)
            descriptor.links.append(new_link)
            working_link_dir.child_descriptors.append(new_link)
            return
    print(f'The file with the name "{name1}" does not exist')


# Function to remove a link to a file
def unlink(name):
    if FileSystemState.is_initialised():
        return
    old_path = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and old_path == '':
        old_path = '/'
    desc_name = name.split('/')[-1]
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f'There is no link on name "{name}", it is a file')
        return
    for descriptor in working_dir.child_descriptors:
        if descriptor.name == desc_name:
            if isinstance(descriptor, Descriptor):
                if descriptor.type == 'directory':
                    print('You can\'t unlink directory')
                working_dir.child_descriptors.remove(descriptor)
                descriptor.nlink -= 1
                if descriptor.nlink == 0:
                    FileSystemState.file_system.descriptors_bitmap[descriptor.id] = 0
                    del descriptor
            else:
                descriptor.descriptor.nlink -= 1
                descriptor.descriptor.links.remove(descriptor)
                working_dir.child_descriptors.remove(descriptor)
                if descriptor.descriptor.nlink == 0:
                    FileSystemState.file_system.descriptors_bitmap[descriptor.descriptor.id] = 0
                    del descriptor.descriptor
            return
    print(f'There is no link on name "{name}"')


# Function to change the size of a file
def truncate(name, size):
    if FileSystemState.is_initialised():
        return
    old_path = "/".join(name.split('/')[:-1])
    if len(name.split('/')) == 2 and old_path == '':
        old_path = '/'
    desc_name = name.split('/')[-1]
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f'There is no directory with the path {old_path}')
        return
    for descriptor in working_dir.child_descriptors:
        if descriptor.name == desc_name and descriptor.type == 'regular':
            if size < descriptor.size:
                num = len(descriptor.blocks)
                # While the total size of the blocks is greater than the new size plus one block size remove the last block from the file
                while num * FileSystemState.block_size > size + FileSystemState.block_size:
                    descriptor.blocks.pop(num - 1)
                    num -= 1
                descriptor.size = size
            if size > descriptor.size:
                num = len(descriptor.blocks) - 1
                for i in range(descriptor.size, size):
                    # If the current byte is the last byte of the current block add a new block to the file
                    if i == FileSystemState.block_size * num + FileSystemState.block_size:
                        descriptor.blocks.append(['\0' for i in range(FileSystemState.block_size)])
                        num += 1
                    # Write a null byte at the current position in the file
                    descriptor.blocks[num][i - num * FileSystemState.block_size] = 0
                descriptor.size = size
            return
    print(f'The file with the name "{name}" does not exist')


def symlink(string, pathname):
    if FileSystemState.is_initialised():
        return
    if FileSystemState.file_system.descriptors_num >= FileSystemState.file_system.descriptors_max_num:
        print('All descriptors are used')
        return
    old_path = "/".join(pathname.split('/')[:-1])
    if len(pathname.split('/')) == 2 and old_path == '':
        old_path = '/'
    new_sym_name = pathname.split('/')[-1]
    if len(str(new_sym_name)) > FileSystemState.max_length:
        print(f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
        return
    if new_sym_name == '':
        print('Name could\'t be empty')
        return
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f"There is no directory with this path: {old_path}")
        return
    for directory in working_dir.child_directories:
        if new_sym_name == directory.name:
            print('Directory with this name exist')
            return
    descriptor_num = None
    for i, value in enumerate(FileSystemState.file_system.descriptors_bitmap):
        if not value:
            FileSystemState.file_system.descriptors_bitmap[i] = 1
            descriptor_num = i
            break
    new_symlink_descriptor = Descriptor(descriptor_num, 'symlink', 0, new_sym_name, string)
    FileSystemState.register_descriptor(new_symlink_descriptor)
    new_symlink = Symlink(new_sym_name, new_symlink_descriptor, working_dir, string)
    working_dir.child_directories.append(new_symlink)
    working_dir.child_descriptors.append(new_symlink_descriptor)


def mkdir(pathname: str):
    if FileSystemState.is_initialised():
        return
    if FileSystemState.file_system.descriptors_num >= FileSystemState.file_system.descriptors_max_num:
        print('All descriptors are used')
        return
    old_path = "/".join(pathname.split('/')[:-1])
    if len(pathname.split('/')) == 2 and old_path == '':
        old_path = '/'
    new_dir_name = pathname.split('/')[-1]
    if len(str(new_dir_name)) > FileSystemState.max_length:
        print(f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
    working_dir = FileSystemState.check_path_exist(old_path)
    if working_dir is None:
        print(f'There is no directory with the path {old_path}')
        return
    for directory in working_dir.child_directories:
        if new_dir_name == directory.name:
            print(f'The directory with the name "{new_dir_name}" already exists')
            return
    descriptor_num = None
    for i, value in enumerate(FileSystemState.file_system.descriptors_bitmap):
        if not value:
            FileSystemState.file_system.descriptors_bitmap[i] = 1
            descriptor_num = i
            break
    new_dir_descriptor = Descriptor(descriptor_num, 'directory', 0, new_dir_name)
    FileSystemState.register_descriptor(new_dir_descriptor)
    new_dir = Dir(new_dir_name, new_dir_descriptor, working_dir)
    working_dir.child_descriptors.append(new_dir_descriptor)
    working_dir.child_directories.append(new_dir)


def rmdir(pathname):
    if FileSystemState.is_initialised():
        return
    if pathname == '/':
        print('You can\'t delete root directory')
        return
    if pathname == '' or pathname == '.':
        print('You can\'t delete current directory')
        return
    if pathname == '..':
        print('You can\'t delete directory that upper then other')
        return
    old_dir = FileSystemState.check_path_exist(pathname)
    if old_dir is None:
        print(f'There is no directory with the path {pathname}')
        return
    if len(old_dir.child_descriptors) != 2:
        print('You can\'t delete nonempty dir')
        return
    if FileSystemState.cwd == old_dir:
        print('You can\'t delete directory you are in now')
    old_dir.parent.child_descriptors.remove(old_dir.descriptor)
    old_dir.parent.child_directories.remove(old_dir)
    old_dir.child_descriptors.clear()
    old_dir.child_directories.clear()
    old_dir.parent.descriptor.nlink -= 1
    FileSystemState.file_system.descriptors.remove(old_dir.descriptor)
    FileSystemState.file_system.descriptors_bitmap[old_dir.descriptor.id] = 0
    FileSystemState.file_system.descriptors_num -= 1
    del old_dir.descriptor
    del old_dir


def cd(pathname):
    if FileSystemState.is_initialised():
        return
    if pathname == '/':
        FileSystemState.cwd = FileSystemState.file_system.root
        return
    new_dir = FileSystemState.check_path_exist(pathname)
    if new_dir is None:
        print(f'There is no directory with the path {pathname}')
        return
    FileSystemState.cwd = new_dir
