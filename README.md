# Práctica 3 - Multicast
## Introducción
En esta práctica se ha desarrollado un módulo de comunicaciones para un servicio de juegos online. Este juego consiste en un sistema de preguntas y respuestas (estilo trivial). Para la obtención de las preguntas y respuestas, se empleará la API https://the-trivia-api.com/. El objetivo es permitir la interacción entre los jugadores y proporcionar anuncios globales sobre diferentes eventos durante el juego. El sistema está diseñado para manejar eventos como el inicio del juego, actualizaciones de puntuaciones, abandono de jugadores, felicitaciones al ganador y el fin del juego. Todo el código del juego se encuentra dentro de la carpeta **Entregable**
## Explicación del código
El código desarrollado se divide en cuatro partes: el servidor, los jugadores (player1 y player2), funciones de multidifusión (multicast_functions), y una interfaz para la API de preguntas y respuestas.

### 1. Servidor (`server.ipynb`)
El servidor es responsable de coordinar la comunicación entre los jugadores y gestionar los eventos del juego. Algunas de sus funciones clave incluyen:
- **Inicialización y configuración del juego**: Inicializa el socket y establece el numero de preguntas y jugadores.
- **Espera de Jugadores:** El servidor espera a que los jugadores se conecten antes de iniciar el juego.
- **Inicio del Juego y comunicaciones con la API:** Inicia el juego después de que se conecten los jugadores, manejando la distribución de preguntas y el seguimiento de las puntuaciones.
- **Finalización del Juego:** Anuncia el fin del juego y felicita al ganador.
La funcion más destacable de este codigo es la iniciar partida, definida en **multicast_functions**.

```
def init_game(sock, num_jugadores, num_preguntas):
        
        # Inicialización de variables
        global puntuaciones
        puntuaciones = {}  # Diccionario para almacenar las puntuaciones de los jugadores
        fin_juego = False  # Variable para controlar el estado del juego
        
        # Anunciar el inicio del juego al grupo de multidifusión
        send_multicast_message(sock, "Server: ¡El juego va a comenzar!\n")
        time.sleep(1)  # Esperar un segundo para asegurar que todos los jugadores reciban el mensaje
        
        # Bucle para cada pregunta del juego
        for i in range(num_preguntas):
        # Enviar mensaje de inicio de ronda al grupo de multidifusión
        send_multicast_message(sock, f"\nRonda {i+1}/{num_preguntas}\n")
        time.sleep(1)  # Esperar un segundo
        
        # Enviar pregunta y esperar respuestas de los jugadores
        question, respuesta_correcta = send_question(sock)
        respuestas = listen_answers(sock, num_jugadores)
        
        # Actualizar puntuaciones según las respuestas de los jugadores
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
        
        # Enviar la respuesta correcta y el ranking actualizado al grupo de multidifusión
        send_multicast_message(sock, "Respuesta correcta: " + respuesta_correcta)
        send_ranking(sock, puntuaciones)
        time.sleep(1)  # Esperar un segundo antes de la siguiente ronda
        
        # Determinar al ganador y enviar mensaje de fin del juego al grupo de multidifusión
        ganador = get_ganador(puntuaciones)
        send_multicast_message(sock, "¡El juego ha terminado! El ganador es " + ganador)
        time.sleep(1)  # Esperar un segundo
        fin_juego = True  # Marcar el fin del juego
```
Esta función controla el flujo del juego, enviando preguntas, recibiendo respuestas de los jugadores, actualizando las puntuaciones y anunciando el ganador al final. Cada paso se comunica al grupo de multidifusión para que todos los jugadores estén informados en tiempo real.

### 2. Jugadores (`player1.ipynb` y `player2.ipynb`)
Cada jugador se conecta al servidor y participa en el juego. Sus responsabilidades son:
- **Unirse al Grupo de Multidifusión:** Los jugadores se unen al grupo de multidifusión para recibir y enviar mensajes.
- **Participación en el Juego:** Responden preguntas, envían mensajes al servidor y a otros jugadores.
- **Manejo de Eventos:** Pueden abandonar la partida, lo que se comunica al servidor y a los demás jugadores.

La complejidad en este codigo se encuentra en poder escuchar mensajes y escribir a la vez, al ser dos procesos independiente se ha obtado hacer uso de un thread.
Además, se crea un hilo para recibir mensajes del grupo de multidifusión y permitir al jugador enviar mensajes mientras espera:
```
        # Crear un hilo para recibir mensajes del grupo de multidifusión
        receive_thread = threading.Thread(target=mf.receive_multicast_messages, args=(multicast_sock, stop_receive_thread))
        receive_thread.start()
        
        # Permitir al usuario enviar mensajes mientras espera
        while not mf.is_partida_terminada():
            message = input("Mensaje: ")
            mf.send_multicast_message(multicast_sock, user + ": " + message)
        
            if message.lower() == "abandono":
                mf.send_multicast_message(multicast_sock, user + " ha abandonado la partida.")
                break
        
        # Indicar al hilo de recepción que debe finalizar
        stop_receive_thread.set()
        # Esperar a que el hilo de recepción termine
        receive_thread.join()
        # Cerrar el socket de multidifusión
        multicast_sock.close()
```
En este fragmento de código, se crea un hilo receive_thread que ejecuta la función mf.receive_multicast_messages() para recibir mensajes del grupo de multidifusión mientras el jugador espera. Mientras tanto, el jugador puede enviar mensajes al grupo utilizando mf.send_multicast_message(). Si el jugador decide abandonar la partida (message.lower() == "abandono"), se envía un mensaje al grupo anunciando su abandono y se finaliza el hilo de recepción. Una vez que se sale del bucle, se cierra el socket de multidifusión.

### 3. Funciones de Multidifusión (`multicast_functions.py`)
Estas funciones facilitan la comunicación entre el servidor y los jugadores a través de la multidifusión. Sus principales características son:
- **Unirse al Grupo de Multidifusión:** Configura y une el socket al grupo de multidifusión.
- **Envío y Recepción de Mensajes:** Envía y recibe mensajes entre el servidor y los jugadores.
- **Notificación de Eventos:** Notifica a los jugadores sobre eventos importantes durante el juego.

La explicación detallada de las funciones join_multicast_group, send_multicast_message, y receive_multicast_messages dentro de multicast_functions.py:
```
        def join_multicast_group():
            """
            Esta función crea un socket UDP y se une al grupo de multidifusión especificado.
            """
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # Crear un socket UDP
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Permitir reutilización de dirección
        
            # Enlazar el socket al grupo de multidifusión
            sock.bind(('', MCAST_PORT))
        
            # Unirse al grupo de multidifusión
            mreq = struct.pack('4sl', socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
            return sock  # Devolver el socket creado y unido al grupo de multidifusión
        
        def send_multicast_message(sock, message):
            """
            Esta función envía un mensaje al grupo de multidifusión utilizando el socket proporcionado.
            """
            # Enviar un mensaje al grupo de multidifusión
            sock.sendto(pickle.dumps(message), (MCAST_GRP, MCAST_PORT))
        
        def receive_multicast_messages(sock, stop_event):
            """
            Esta función recibe mensajes del grupo de multidifusión utilizando el socket proporcionado,
            deteniéndose cuando se activa el evento de parada (stop_event).
            """
            while not stop_event.is_set():
                # Recibir mensajes del grupo de multidifusión
                data, addr = sock.recvfrom(1024)
                message = pickle.loads(data)
                if message:  # Comprobar si el mensaje no está vacío
                    print(message)  # Imprimir el mensaje recibido
                    if fin_juego:  # Verificar si se ha terminado el juego
                        stop_event.set()  # Establecer el evento de parada para detener la recepción de mensajes
                        break  # Salir del bucle de recepción
```
Estas funciones forman la base de la comunicación mediante multidifusión en el juego. join_multicast_group crea un socket UDP y se une al grupo de multidifusión especificado. send_multicast_message envía un mensaje al grupo de multidifusión utilizando el socket proporcionado. receive_multicast_messages recibe mensajes del grupo de multidifusión utilizando el socket proporcionado, deteniéndose cuando se activa el evento de parada. Estas funciones son esenciales para la comunicación entre el servidor y los jugadores durante el juego.

### 4. Interfaz para la API de Preguntas y Respuestas (`API.py`)
Esta interfaz se encarga de obtener preguntas aleatorias de una API externa. Sus funciones incluyen:
- **Obtención de Preguntas:** Llama a la API para obtener preguntas y respuestas.
- **Almacenamiento de Preguntas:** Guarda las preguntas en un diccionario para su uso en el juego.
- **Selección de Preguntas Aleatorias:** Selecciona preguntas aleatorias para enviar a los jugadores.
```
          def get_pregunta_aleatoria():
            """
            Esta función selecciona aleatoriamente una pregunta del diccionario de preguntas y respuestas,
            prepara las posibles respuestas y la respuesta correcta, y las devuelve en un diccionario.
            """
            pregunta_texto = random.choice(list(preguntas_dict.keys()))  # Selecciona aleatoriamente una pregunta
            pregunta_info = preguntas_dict[pregunta_texto]  # Obtiene la información de la pregunta seleccionada
            posibles_respuestas = [pregunta_info["Correct Answer"]] + pregunta_info["Incorrect Answers"]  # Prepara las posibles respuestas
            respuesta_correcta = pregunta_info["Correct Answer"]  # Obtiene la respuesta correcta
            random.shuffle(posibles_respuestas)  # Mezcla las respuestas para evitar un orden predecible
            return {
                "Pregunta": pregunta_texto,
                "Posibles Respuestas": posibles_respuestas,
                "Respuesta Correcta": respuesta_correcta
            }
        
        def check_respuesta(pregunta, respuesta):
            """
            Esta función verifica si la respuesta proporcionada por el jugador es correcta para la pregunta dada.
            """
            pregunta_info = preguntas_dict[pregunta]  # Obtiene la información de la pregunta
            return respuesta == pregunta_info["Correct Answer"]  # Compara la respuesta del jugador con la respuesta correcta
```
Estas funciones se encargan de manejar las preguntas y respuestas en el juego. get_pregunta_aleatoria selecciona aleatoriamente una pregunta del diccionario de preguntas y prepara las posibles respuestas y la respuesta correcta, devolviéndolas en un diccionario. Por otro lado, check_respuesta verifica si la respuesta proporcionada por el jugador es correcta para una pregunta dada. Ambas funciones son esenciales para el funcionamiento del juego al gestionar las preguntas y validar las respuestas de los jugadores.

## Ejecución del código 
1. Abre una terminal o línea de comandos en tu sistema.

2. Clona el repositorio con el siguiente comando:

    ```
    git clone https://github.com/202006359/Practica-3-Multicast.git
    ```

3. Inicializa el servidor Jupyter Notebook desde Anaconda.
<img width="249" alt="image" src="https://github.com/202006359/Practica-1-UDP/assets/113789409/8347b6ac-c6fb-42b4-8620-f8b7634689c4">

  
5. Esto abrirá una ventana del navegador web con el panel de control de Jupyter Notebook. Desde aquí, dirigite a la proyecto Practica-3-Multicast y picha en la carpeta "Entregable". A continuación, abre el archivo "server.ipynb", "player1.ipynb" y "player2.ipynb" (la partida a modo de tutorial será con dos jugadores).  

6. Ejecuta el código del servidor en Jupyter Notebook ejecutando todas las celdas de código en "server.ipynb". Selecciona el numero de jugadores (2 para este tutorial) y el numero de preguntas que deberan resolver los jugadores antes de que finalize la partida.

7. Ejecuta el código del cliente en Jupyter Notebook ejecutando todas las celdas de código en "player1.ipynb". Introduzca el nombre de usuario.

8. Ejecuta el código del cliente en Jupyter Notebook ejecutando todas las celdas de código en "player2.ipynb". Introduzca el nombre de usuario.

9. Una vez los jugadores hayan elegido su username, deberán escribir *Ready to play* para que comience la partida.

10. Si un jugador quisiera abandonar la partida, es tan sencillo como escribir *abandono* en el chat del juego.

11. Una vez los jugadores hayan respondido todas las preguntas, recibirán el ranking final y se terminará la partida.

## Capturas de pantalla
### Player 1
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/cd65737b-65ba-4b7c-9fac-de8ba4368549">
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/5857fbf5-aa0a-431f-8007-fd981319c06b">

### Player 2
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/2cc26c83-f66d-4637-bccd-ae499a6a77c5">
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/f1e709ad-99f6-4fd6-add0-f965a9ad862d">

### Servidor
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/1b183afc-982e-4b52-bf43-7b5a94f3b001">


