from file_system_state import FileSystemState
from descriptor import Descriptor, Link
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
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name:
            descriptor.show()
            return
    print(f'The file with the name "{name}" does not exist')


# Function to list all the files in the file system
def ls():
    if FileSystemState.is_initialised():
        return
    table = PrettyTable()
    table.field_names = ["id", "name", "type", "nlink", "size", "nblock"]
    for descriptor in FileSystemState.file_system.descriptors:
        if isinstance(descriptor, Descriptor):
            table.add_row([descriptor.id, descriptor.name, descriptor.type, descriptor.nlink, descriptor.size, len(descriptor.blocks)])
        else:
            table.add_row([descriptor.descriptor.id, descriptor.name + '->' + descriptor.descriptor.name, descriptor.descriptor.type, descriptor.descriptor.nlink, descriptor.descriptor.size, len(descriptor.descriptor.blocks)])
    print(table)


# Function to create a file with a given name
def create(name):
    if FileSystemState.is_initialised():
        return
    if len(str(name)) > FileSystemState.max_length:
        print(
            f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
    if FileSystemState.file_system.descriptors_num >= FileSystemState.file_system.descriptors_max_num:
        print('All descriptors are used')
        return
    for descriptor in FileSystemState.file_system.descriptors:
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
    descriptor = Descriptor(descriptor_num, 'regular', 0, name)
    FileSystemState.file_system.descriptors.append(descriptor)
    FileSystemState.file_system.descriptors_num += 1


# Function to open a file with a given name
def open_file(name):
    if FileSystemState.is_initialised():
        return
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name:
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
    if len(str(name2)) > FileSystemState.max_length:
        print(
            f'The file name is too long, please create a file name no longer than {FileSystemState.max_length} characters')
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name2:
            print(f'The file with the name "{name2}" already exists')
            return
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name1:
            new_link = Link(descriptor, name2)
            descriptor.links.append(new_link)
            FileSystemState.file_system.descriptors.append(new_link)
            return
    print(f'The file with the name "{name1}" does not exist')


# Function to remove a link to a file
def unlink(name):
    if FileSystemState.is_initialised():
        return
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name:
            if isinstance(descriptor, Descriptor):
                print(f'There is no link on name "{name}"')
                return
            else:
                descriptor.descriptor.nlink -= 1
                FileSystemState.file_system.descriptors.remove(descriptor)
                return
    print(f'There is no link on name "{name}"')


# Function to change the size of a file
def truncate(name, size):
    if FileSystemState.is_initialised():
        return
    for descriptor in FileSystemState.file_system.descriptors:
        if descriptor.name == name:

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
