# Scriptcito Chat: Encrypted TCP Communication

Scriptcito es una herramienta de chat cliente-servidor escrita en Python que implementa un sistema de comunicación cifrada de extremo a extremo (E2EE). Utiliza un esquema de criptografía híbrida para garantizar la confidencialidad e integridad de los mensajes.
🚀 Características

    Cifrado Híbrido: Intercambio de llaves mediante RSA-2048 y cifrado de mensajes con AES-128 GCM.

    Autenticación de Datos: Uso de AES-GCM (Galois/Counter Mode) para asegurar que los mensajes no sean alterados en tránsito.

    Interfaz Minimalista: Salida por terminal con códigos de colores ANSI para una mejor legibilidad.

    Multihilo: Manejo de recepción y envío de mensajes de forma asíncrona mediante threading.

🛠️ Requerimientos

    Python 3

    Librerías: cryptography threading os

Puedes instalar las dependencias con:
``pip install -r requirements.txt``

📖 Modo de Uso

    Servidor: Ejecuta scriptcito-server.py, ingresa la IP para escuchar (ej. 0.0.0.0) y define el puerto.

    Cliente: Ejecuta scriptcito-client.py, ingresa la IP del servidor y el mismo puerto.

    Handshake: El servidor enviará su clave pública RSA; el cliente generará una clave AES, la cifrará con la pública del servidor y se la enviará de vuelta.

    Chat: Una vez establecido el túnel cifrado, pueden intercambiar mensajes en tiempo real.
    Usa !exit para cerrar la conexión.

Nota:
>    La idea original era usar cifrado simetrico pero la cosa se complico XD

Fin :3 
