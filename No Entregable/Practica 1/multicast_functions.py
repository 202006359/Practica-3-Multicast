import socket
import struct

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007

def join_multicast_group():
    # Crear un socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Enlazar el socket al grupo de multidifusión
    sock.bind(('', MCAST_PORT))

    # Unirse al grupo de multidifusión
    mreq = struct.pack('4sl', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
    return sock

def send_multicast_message(sock, message):
    # Enviar un mensaje de saludo al grupo
    sock.sendto(str.encode(message), (MCAST_GRP, MCAST_PORT))

def receive_multicast_messages(sock):
    while True:
        # Recibir mensajes del grupo de multidifusión
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        print("Mensaje recibido:", message)
        
        # Si se recibe "Adiós", salir del bucle
        if message == "Adios":
            break


