#!/usr/bin/python3

import socket, threading

#variables
user = "cliente" # cambiar por el que quieras
running = True
ip_destino = input("Ingrese la IP del servidor: ")
puerto_input = input("Ingrese el puerto (por defecto 5000) ")

try:
    puerto = int(puerto_input.lower()) if puerto_input else 5000
except ValueError:
    print("puerto invalido, usando 5000.")
    puerto = 5000

def recibir(s):
    global running
    while running:
        try:
            data = s.recv(1024)
            if not data:
                print("\n[System] el servidor cerro la conexion\n Presione ENTER para salir del script.\nBye...")
                running = False
                break
            print(f"\n[Servidor]: {data.decode()}")
            print(f"[{user}] > ", end="", flush=True)
        except Exception as f:
            print(f"Error: {f}")
            running = False
            break

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    try:
        s.connect((ip_destino, puerto))
        print(f"[+] Conectado a {ip_destino}")
        threading.Thread(target=recibir, args=(s,), daemon=True).start()
        while running:
            try:
                msg = input(f"[{user}] > ")
                if not running:
                    break
                if msg.lower() in ["!exit", "!quit"]:
                    print("Bye...")
                    running = False
                    break
                s.sendall(msg.encode())
            except (BrokenPipeError, OSError):
                print("[System] Conexion cerrada del lado del servidor.\nPresione ENTER para salir del script.\nBye...")
                running = False
                break
    except Exception as e:
        print(f"Error al conectar: {e}")
#LO MISMO EN ESTE