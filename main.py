from commands import mkfs, stat, ls, create, link, unlink, open_file, close, seek, write, read, truncate
from file_system_state import FileSystemState


def check_state():
    if FileSystemState.file_system is None:
        print('The file system is not initialised')
        return 1
    return 0


while True:
    try:
        input_array = input('> ').split(' ')
        command = input_array[0]
        if command == 'mkfs':
            mkfs(int(input_array[1]))
        elif command == 'stat':
            stat(input_array[1])
        elif command == 'ls':
            ls()
        elif command == 'create':
            create(input_array[1])
        elif command == 'open':
            open_file(input_array[1])
        elif command == 'close':
            close(int(input_array[1]))
        elif command == 'seek':
            seek(int(input_array[1]), int(input_array[2]))
        elif command == 'read':
            read(int(input_array[1]), int(input_array[2]))
        elif command == 'write':
            write(int(input_array[1]), int(input_array[2]), input_array[3])
        elif command == 'link':
            link(input_array[1], input_array[2])
        elif command == 'unlink':
            unlink(input_array[1])
        elif command == 'truncate':
            truncate(input_array[1], int(input_array[2]))
        elif command == 'exit':
            exit(0)
        else:
            print('Unknown command')
    except NameError as error:
        print('Error in function name')
    except SyntaxError as error:
        print('Syntax error')
    except TypeError as error:
        print('Arguments error')
    except ValueError as error:
        print('Value error')
