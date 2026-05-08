#!/usr/bin/python3

# Imports
import socket
import threading
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# colores
ROJO = "\033[91m"
VERDE = "\033[92m"
AZUL = "\033[94m"
RESET = "\033[0m"

# variables
user = "servidor"
running = True
client_ip = input("Ingrese la IP para ESCUCHAR (ej. 0.0.0.0): ")
puerto_input = input("Desea especificar un puerto? (por defecto 5000): ")

# generar claves RSA
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)
public_key = private_key.public_key()

# validar puerto
try:
    client_port = int(puerto_input.lower()) if puerto_input else 5000
    if client_port not in range(1, 65536):
        print(f"{ROJO}[-]{RESET} Puerto fuera de rango, usando 5000.")
        client_port = 5000
except ValueError:
    print(f"{ROJO}[-]{RESET} Puerto invalido, usando 5000.")
    client_port = 5000

def encrypt_message(aes_key, plaintext):
    aesgcm = AESGCM(aes_key)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode(), None)
    return nonce + ciphertext

def decrypt_message(aes_key, data):
    aesgcm = AESGCM(aes_key)
    nonce = data[:12]
    ciphertext = data[12:]
    return aesgcm.decrypt(nonce, ciphertext, None).decode()

# recibir mensajes (aún sin AES)
def recibir(conn):
    global running
    while running:
        try:
            data = conn.recv(1024)
            if not data:
                print(f"\n{ROJO}[-]{RESET} Cliente desconectado. Pulse ENTER para salir.")
                running = False
                break
            try:                
                mensaje = decrypt_message(aes_key, data)
                print(f"\n{VERDE}[Cliente]{RESET}: {mensaje}")
                print(f"{AZUL}[{user}] > {RESET}", end="", flush=True)
            except Exception as e:
                print(f"\n{ROJO}[!] Error al desencriptar mensaje{RESET} - {e}")

        except Exception as e:
            print(f"\n{ROJO}[-]{RESET} Error recibiendo: {e}")
            running = False
            break

# socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        s.bind((client_ip, client_port))
        s.listen()
        print(f"{AZUL}[*]{RESET} Escuchando en: {client_port}")

        conn, addr = s.accept()

        with conn:
            print(f"{VERDE}[+]{RESET} Conectado con {addr[0]}:{addr[1]}")

            # enviar clave pública
            public_key_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            conn.sendall(public_key_pem)

            print(f"{VERDE}[+]{RESET} Clave pública enviada")

            # recibir AES cifrada
            encrypted_aes_key = conn.recv(4096)

            if not encrypted_aes_key:
                print(f"{ROJO}[-]{RESET} No se recibió AES key")
                exit(1)

            # descifrar AES
            aes_key = private_key.decrypt(
                encrypted_aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            print(f"{VERDE}[+]{RESET} AES recibida correctamente ({len(aes_key)} bytes)")

            # hilo receptor
            threading.Thread(target=recibir, args=(conn,), daemon=True).start()

            # loop envío
            while running:
                try:
                    mensaje = input(f"{AZUL}[{user}] > {RESET}")

                    if not running:
                        break

                    if mensaje.lower() in ["!exit", "!quit"]:
                        print(f"{AZUL}Bye...{RESET}")
                        running = False
                        break
                    # cifrar mensaje con AES
                    encrypt = encrypt_message(aes_key, mensaje)
                    conn.sendall(encrypt)

                except (BrokenPipeError, OSError):
                    print(f"{ROJO}[-]{RESET} Conexión cerrada")
                    running = False
                    break

    except Exception as e:
        print(f"Error: {e}")
        exit(1)
