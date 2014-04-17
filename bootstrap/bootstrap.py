import os
import socket


if __name__ == '__main__':
    # Remove the bootstrap batch script.
    os.unlink('C:\\bootstrap.bat')

    s = socket.create_connection(('192.168.56.1', 61453))
