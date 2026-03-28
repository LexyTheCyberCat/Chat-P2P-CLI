#!/usr/bin/python3

import socket
import threading

# variables
user = "servidor"
running = True

client_ip = input("Ingrese la IP para ESCUCHAR (ej. 0.0.0.0): ")
puerto_input = input("Desea especificar un puerto? (por defecto 5000): ")

if not puerto_input:
    client_port = 5000
else:
    client_port = int(puerto_input)

def recibir(conn):
    global running
    while running:
        try:
            data = conn.recv(1024)
            if not data:
                print("\n[Servidor] El cliente cerró la conexión.\nPresione ENTER para salir.\nBye...")
                running = False
                break
            print(f"\n[Mensaje recibido]: {data.decode()}")
            print(f"[{user}] > ", end="", flush=True)
        except Exception as e:
            print(f"\nError recibiendo: {e}")
            running = False
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        s.bind((client_ip, client_port))
        s.listen()
        print(f"Escuchando en el puerto {client_port}...")
        
        conn, addr = s.accept()

        with conn:
            print(f"Conectado con: {addr}")
            hilo_receptor = threading.Thread(target=recibir, args=(conn,), daemon=True)
            hilo_receptor.start()
            
            while running:
                try:
                    mensaje = input(f"[{user}] > ")
                    if not running:
                        break
                    if mensaje.lower() in ["!exit", "!quit"]:
                        print("Bye...")
                        running = False
                        break
                    conn.sendall(mensaje.encode("utf-8"))
                except (BrokenPipeError, OSError):
                    print("\n[Servidor] Conexion cerrada.\nPresione ENTER para salir.\nBye...")
                    running = False
                    break

    except Exception as e:
        print(f"Error: {e}")
        exit(1)