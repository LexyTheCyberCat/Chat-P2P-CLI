#!/usr/bin/python3

# Imports
import os
import socket
import threading
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding

# colores
ROJO = "\033[91m"
VERDE = "\033[92m"
AZUL = "\033[94m"
RESET = "\033[0m"

# variables
user = "client"
running = True
ip_destino = input("Ingrese la IP del servidor: ")
puerto_input = input("Ingrese el puerto (por defecto 5000): ")

# Validar nombre de usuario
if not user.isalnum() or len(user) > 20:
    print(f"{ROJO}[!]{RESET} Nombre de usuario inválido.Debe ser alfanumérico y no exceder 20 caracteres.")
    exit(1)
if user.lower() in ["servidor", "cliente", "server", "client"]:
    print(f"{ROJO}[!]{RESET} Esta utilizando un nombre de usuario por defecto, puede cambiarlo modificando la variable 'user'.")

# validar puerto
try:
    puerto = int(puerto_input.lower()) if puerto_input else 5000
    if puerto not in range(1, 65536):
        print(f"{ROJO}[-]{RESET} Puerto fuera de rango, usando 5000.")
        puerto = 5000
except ValueError:
    print(f"{ROJO}[-]{RESET} Puerto invalido, usando 5000.")
    puerto = 5000

# Encriptar mensaje con AES
def encrypt_message(aes_key, plaintext):
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext

# Desencriptar mensaje con AES
def decrypt_message(aes_key, data):
    aesgcm = AESGCM(aes_key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

# recibir clave pública
def recibir_clave_publica(s):
    try:
        data = s.recv(2048)
        if not data:
            print(f"{ROJO}No se recibió la clave pública.{RESET}")
            return None
        
        public_key = serialization.load_pem_public_key(data)
        return public_key

    except Exception as e:
        print(f"Error al recibir clave pública: {e}")
        return None

# recibir mensajes (todavía en texto plano)
def recibir(s):
    global running
    while running:
        try:
            data = s.recv(1024)
            if not data:
                print(f"\n{AZUL}[System]{RESET} {ROJO}Servidor cerró conexión. Pulse ENTER para salir.{RESET}")
                s.close()
                running = False
                break

            try:
                mensaje = decrypt_message(aes_key, data)
                print(f"{mensaje}")
                print(f"{AZUL}[{user}] > {RESET}", end="", flush=True)

            except Exception as e:
                print(f"\n{ROJO}[!] Error al desencriptar mensaje{RESET}")

        except Exception as e:
            print(f"\n{ROJO}[-]{RESET} Error recibiendo: {e}")
            s.close()
            running = False
            break

# conexión
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((ip_destino, puerto))
        print(f"{VERDE}[+]{RESET} Conectando a {ip_destino}:{puerto}")

        # HANDSHAKE
        public_key = recibir_clave_publica(s)

        if public_key is None:
            s.close()
            exit(1)

        print(f"{VERDE}[+]{RESET} Clave pública recibida")

        # generar AES
        aes_key = AESGCM.generate_key(bit_length=128)

        # cifrar AES con RSA
        encrypted_key = public_key.encrypt(
            aes_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )

        # enviar AES cifrada
        s.sendall(encrypted_key)

        print(f"{VERDE}[+]{RESET} AES enviada correctamente")

        # arrancar recepción
        threading.Thread(target=recibir, args=(s,), daemon=True).start()
        
        # loop chat
        while running:
            try:
                mensaje = input(f"{AZUL}[{user}] > {RESET}")
                msg = f"\n{AZUL}[{user}] > {RESET}" + mensaje
                if not running:
                    break
                if mensaje.lower() in ["!exit", "!quit"]:
                    print(f"{AZUL}Bye...{RESET}")
                    s.close()
                    running = False
                    break

                # encriptar en AES y enviar
                encrypt = encrypt_message(aes_key, msg)
                s.sendall(encrypt)

            except (BrokenPipeError, OSError):
                print(f"{ROJO}[-]{RESET} Conexión cerrada por el servidor.")
                s.close()
                running = False
                break
        s.close()

    except Exception as e:
        print(f"Error al conectar: {e}")
        s.close()
        exit(1)
s.close()
exit(0)