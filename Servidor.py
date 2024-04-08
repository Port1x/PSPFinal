import socket
import threading
import json
import mysql.connector
from time import sleep

client_connections = []

def handle_client(connection, address, db_config):
    print(f"Conexión desde {address}")
    with connection:
        client_connections.append(connection)
        while True:
            try:
                data = connection.recv(1024).decode()
                if not data:
                    break
                
                if data == '1':
                    # Opción 1: Consultar las tres primeras sentencias sin el campo texto
                     query = "SELECT id, cendoj_id, tribunal, sala, sede, seccion, fecha, recurso_n, juez, letrado, delito FROM sentencias LIMIT 3"
                elif data == '2':
                    # Opción 2: Consultar las tres primeras sentencias agrupadas por tipo de delito
                    query = "SELECT cendoj_id, delito, juez FROM sentencias GROUP BY delito, cendoj_id, juez ORDER BY delito LIMIT 3"
                elif data == '3':
                    # Opción 3: Consultar sentencia por ID
                    id_solicitud = connection.recv(1024).decode()
                    query = f"SELECT id, cendoj_id, tribunal, sala, sede, seccion, fecha, recurso_n, juez, letrado, delito FROM sentencias WHERE id = {id_solicitud}"
                elif data == '4':
                    # Opción 4: Consultar el texto de una sentencia
                    id_solicitud = connection.recv(1024).decode()
                    query = f"SELECT texto_completo FROM sentencias WHERE id = {id_solicitud}"
                else:
                    continue
                
                # Ejecutar la consulta
                with mysql.connector.connect(**db_config) as conn, conn.cursor(dictionary=True) as cursor:
                    cursor.execute(query)
                    if cursor.description:
                        rows = cursor.fetchall()
                        response = json.dumps(rows)
                    else:
                        response = "Consulta ejecutada."
                    connection.sendall(response.encode())

            except Exception as e:
                print(f"Error al manejar la conexión con {address}: {str(e)}")
                break


def start_server(host, port, db_config):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((host, port))
        server.listen()
        print(f"Servidor escuchando en {host}:{port}")

        while True:
            connection, address = server.accept()
            client_thread = threading.Thread(target=handle_client, 
                                             args=(connection, address, db_config))
            client_thread.start()

if __name__ == "__main__":
    HOST = '10.10.10.20'
    PORT = 65432
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': 'pirineus',
        'database': 'sentencias'
    }

    start_server(HOST, PORT, DB_CONFIG)
