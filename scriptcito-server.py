#!/usr/bin/python3

import socket
import threading

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

# validar puerto
try:
    client_port = int(puerto_input.lower()) if puerto_input else 5000
except ValueError:
    print(f"{ROJO}Puerto invalido, usando 5000.{RESET}")
    client_port = 5000

# Funcion para recibir mensajes del cliente
def recibir(conn):
    global running
    while running:
        try:
            # Si el cliente cierra la conexión, data será vacío
            data = conn.recv(1024)
            if not data:
                print(f"\n{AZUL}[Servidor]{RESET} {ROJO}El cliente cerró la conexión.\nPresione ENTER para salir.{RESET}\n{AZUL}Bye...{RESET}")
                running = False
                break

            print(f"\n{VERDE}[Cliente]{RESET}: {data.decode()}")
            print(f"{AZUL}[{user}] > {RESET}", end="", flush=True)

        except Exception as e:
            print(f"\nError recibiendo: {e}")
            running = False
            break

# Configuración del socket
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind((client_ip, client_port))
        s.listen()
        print(f"Escuchando en el puerto {client_port}...")     

        conn, addr = s.accept()

        with conn:
            print(f"{VERDE}[+]{RESET} Conectado con {addr[0]}:{addr[1]}")
            hilo_receptor = threading.Thread(target=recibir, args=(conn,), daemon=True)
            hilo_receptor.start()
            
            # Loop principal para enviar mensajes al cliente
            while running:
                try:
                    mensaje = input(f"{AZUL}[{user}] > {RESET}")
                    if not running:
                        break

                    if mensaje.lower() in ["!exit", "!quit"]:
                        print(f"{AZUL}Bye...{RESET}")
                        running = False
                        break

                    conn.sendall(mensaje.encode("utf-8"))
                    
                except (BrokenPipeError, OSError):
                    print(f"\n{AZUL}[Servidor] {ROJO}Conexion cerrada.\nPresione ENTER para salir.{RESET}\n{AZUL}Bye...{RESET}")
                    running = False
                    break

    except Exception as e:
        print(f"Error: {e}")
        exit(1)

# NO TOCAR, NO SE COMO FUNCIONA EL CODIGO DE ARRIBA, SI LO TOCO SE ROMPE, ASI QUE MEJOR NO LO TOCO.
