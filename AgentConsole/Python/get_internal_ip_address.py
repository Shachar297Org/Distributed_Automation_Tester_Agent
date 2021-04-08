import socket

internal_ip = socket.gethostbyname(socket.gethostname())
print(internal_ip)
