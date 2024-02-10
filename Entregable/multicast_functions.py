import socket
import struct
import time
import API as api
import pickle

MCAST_GRP = '224.1.1.1'
MCAST_PORT = 5007
fin_juego = False

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
    sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))

def receive_multicast_messages(sock, stop_event):
    while not stop_event.is_set():
        # Recibir mensajes del grupo de multidifusión
        data, addr = sock.recvfrom(1024)
        message = pickle.loads(data)
        if message:  # Check if the message is not empty 
            print(message)
            if fin_juego:
                stop_event.set()
                break
            
def is_partida_terminada():
    return fin_juego

#Esperar a que se conecten los jugadores  
def wait_for_players(sock, num_jugadores):
    print("Esperando a que se conecten los jugadores...")
    count_jugadores = 0 
    while count_jugadores < num_jugadores:
        data, addr = sock.recvfrom(4096)
        message = pickle.loads(data)
        try:
            jugador = message.split(":")[0]
            if message.split(":")[1].strip() == "Ready to play":
                count_jugadores += 1
                send_multicast_message(sock, f"Server: ¡Bienvenido a la partida {jugador}!")
        except:
            continue
    send_multicast_message(sock, "\n¡Todos los jugadores están listos para jugar!\n")

def init_game(sock, num_jugadores, num_preguntas):
    global puntuaciones
    puntuaciones = {}
    fin_juego = False
    
    send_multicast_message(sock, "Server: ¡El juego va a comenzar!\n")
    time.sleep(1)
    for i in range(num_preguntas):
        send_multicast_message(sock, f"\nRonda {i+1}/{num_preguntas}\n")
        time.sleep(1)
        #Enviar pregunta
        question, respuesta_correcta = send_question(sock)
        #Esperar respuestas
        respuestas = listen_answers(sock, num_jugadores)
        #Actualizar puntuaciones
        for jugador in respuestas.keys():
            respuesta = respuestas[jugador]
            if respuesta == respuesta_correcta:
                if jugador in puntuaciones:
                    puntuaciones[jugador] += 1
                else:
                    puntuaciones[jugador] = 1
            else:
                if jugador in puntuaciones:
                    puntuaciones[jugador] += 0
                else:
                    puntuaciones[jugador] = 0
        send_multicast_message(sock, "Respuesta correcta: " + respuesta_correcta)
        #Enviar ranking
        send_ranking(sock, puntuaciones)
        time.sleep(1)
    ganador = get_ganador(puntuaciones)
    send_multicast_message(sock, "¡El juego ha terminado! El ganador es " + ganador)
    time.sleep(1)
    fin_juego = True

def send_question(sock):
    question_info = api.get_pregunta_aleatoria()
    question_text = question_info["Pregunta"]
    possible_answers = question_info["Posibles Respuestas"]
    correct_answer = question_info["Respuesta Correcta"]
    send_multicast_message(sock, question_text)
    send_multicast_message(sock, possible_answers)
    return question_text, correct_answer

def listen_answers(sock, num_jugadores):
    respuestas = {}
    print("Esperando a que los jugadores respondan...")
    while len(respuestas) < num_jugadores:
        data, addr = sock.recvfrom(1024)
        if data.strip():
            message = pickle.loads(data)
            try:
                jugador, respuesta = message.split(":", 1)
                jugador = jugador.strip()
                respuesta = respuesta.strip()
                if jugador.startswith("user") and respuesta:
                    respuestas[jugador] = respuesta
                    print(f"{jugador} respondió: {respuesta}")
            except:
                continue
    return respuestas

def send_ranking(sock, puntuaciones):
    ranking = sorted(puntuaciones.items(), key=lambda x: x[1], reverse=True)
    message = "Ranking:\n"
    for i, (player, score) in enumerate(ranking):
        message += f"{i+1}. {player}: {score}\n"
    send_multicast_message(sock, message)

def get_ganador(puntuaciones):
    ganador = max(puntuaciones, key=puntuaciones.get)
    return ganador

