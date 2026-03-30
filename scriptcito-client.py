#!/usr/bin/python3

import socket, threading

# colores
ROJO = "\033[91m"
VERDE = "\033[92m"
AZUL = "\033[94m"
RESET = "\033[0m"

#variables
user = "cliente" # cambiar por el que quieras
running = True
ip_destino = input("Ingrese la IP del servidor: ")
puerto_input = input("Ingrese el puerto (por defecto 5000): ")

# validar puerto
try:
    puerto = int(puerto_input.lower()) if puerto_input else 5000
except ValueError:
    print(f"{ROJO}Puerto invalido, usando 5000.{RESET}")
    puerto = 5000

# funcion para recibir mensajes del servidor
def recibir(s):
    global running
    while running:
        try:
            # Si el servidor cierra la conexión, data será vacío
            data = s.recv(1024)
            if not data:
                print(f"\n{AZUL}[System] {ROJO}el servidor cerro la conexion\n Presione ENTER para salir del script.{RESET}\n{AZUL}Bye...{RESET}")
                running = False
                break
            
            print(f"\n{AZUL}[Servidor]{RESET}: {data.decode()}")
            print(f"{AZUL}[{user}] > {RESET}", end="", flush=True)
            
        except Exception as f:
            print(f"Error: {f}")
            running = False
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((ip_destino, puerto))
        print(f"{VERDE}[+]{RESET} Conectado a {ip_destino}:{puerto}")
        threading.Thread(target=recibir, args=(s,), daemon=True).start()

        # Loop principal para enviar mensajes al servidor
        while running:
            try:
                msg = input(f"{AZUL}[{user}] > {RESET}")
                
                if not running:
                    break

                if msg.lower() in ["!exit", "!quit"]:
                    print(f"{AZUL}Bye...{RESET}")
                    running = False
                    break
                s.sendall(msg.encode())
            
            except (BrokenPipeError, OSError):
                print(f"{AZUL}[System] {ROJO}Conexion cerrada del lado del servidor.\nPresione ENTER para salir del script.{RESET}\n{AZUL}Bye...{RESET}")
                running = False
                break

    except Exception as e:
        print(f"Error al conectar: {e}")

# LO MISMO CON ESTE
