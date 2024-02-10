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

def receive_multicast_messages(sock, stop_event):
    while not stop_event.is_set():
        # Recibir mensajes del grupo de multidifusión
        data, addr = sock.recvfrom(1024)
        message = data.decode('utf-8')
        if message.strip():  # Check if the message is not empty (strip removes leading/trailing whitespace)
            print(message)

        if message.strip().lower() == "adios":
            stop_event.set()  # Set the event flag to stop the loop
            break



