# Práctica 3 - Multicast
## Introducción
En esta práctica se ha desarrollado un módulo de comunicaciones para un servicio de juegos online. Este juego consiste en un sistema de preguntas y respuestas (estilo trivial). Para la obtención de las preguntas y respuestas, se empleará la API https://the-trivia-api.com/. El objetivo es permitir la interacción entre los jugadores y proporcionar anuncios globales sobre diferentes eventos durante el juego. El sistema está diseñado para manejar eventos como el inicio del juego, actualizaciones de puntuaciones, abandono de jugadores, felicitaciones al ganador y el fin del juego. Todo el código del juego se encuentra dentro de la carpeta **Entregable**
## Explicación del código
El código desarrollado se divide en cuatro partes: el servidor, los jugadores (player1 y player2), funciones de multidifusión (multicast_functions), y una interfaz para la API de preguntas y respuestas.

### 1. Servidor (`server.ipynb`)
El servidor es responsable de coordinar la comunicación entre los jugadores y gestionar los eventos del juego. Algunas de sus funciones clave incluyen:
- Inicialización y configuración del juego, e.g. numero de preguntas, numero de jugadores...
- Espera de jugadores.
- Envío de anuncios sobre el inicio y fin del juego.
- Gestión de las rondas de preguntas y respuestas.
- Mantenimiento de un registro de puntuaciones y determinación del ganador.
- Comunicaciones con la API.

### 2. Jugadores (`player1.ipynb` y `player2.ipynb`)
Cada jugador se conecta al servidor y participa en el juego. Sus responsabilidades son:
- Unirse al grupo de multidifusión y enviar mensajes al servidor y a otros jugadores.
- Participar en las rondas de preguntas y respuestas.
- Interactuar en eventos como el inicio y abandono de la partida.

### 3. Funciones de Multidifusión (`multicast_functions.py`)
Estas funciones facilitan la comunicación entre el servidor y los jugadores a través de la multidifusión. Sus principales características son:
- Unirse al grupo de multidifusión y enviar mensajes.
- Recibir mensajes del grupo de multidifusión y procesarlos.
- Notificar sobre eventos importantes durante el juego.

### 4. Interfaz para la API de Preguntas y Respuestas (`API.py`)
Esta interfaz se encarga de obtener preguntas aleatorias de una API externa. Sus funciones incluyen:
- Llamar a la API para obtener preguntas y respuestas.
- Almacenar las preguntas en un diccionario para su posterior uso en el juego.
- Proporcionar funciones para obtener preguntas aleatorias y verificar respuestas.

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
#### Player 1
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/cd65737b-65ba-4b7c-9fac-de8ba4368549">
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/5857fbf5-aa0a-431f-8007-fd981319c06b">

#### Player 2
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/2cc26c83-f66d-4637-bccd-ae499a6a77c5">
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/f1e709ad-99f6-4fd6-add0-f965a9ad862d">

#### Servidor
<img width="582" alt="image" src="https://github.com/202006359/Practica-3-Multicast/assets/113789409/1b183afc-982e-4b52-bf43-7b5a94f3b001">


