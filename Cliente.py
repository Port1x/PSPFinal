import socket
import json

def send_request(s, message):
    # Envía una solicitud al servidor.
    s.sendall(message.encode())

def receive_response(s):
    # Recibe la respuesta del servidor.
    response = ''
    while True:
        part = s.recv(1024).decode()
        response += part
        if len(part) < 1024:
            break
    print("Respuesta del servidor:")
    return response

def process_response(response, option):
    # Procesa la respuesta dependiendo de la opción seleccionada.
    if option == '4':
        # Para la opción 4, guarda el texto en un archivo.
        try:
            # Intenta formatear el texto si está en formato JSON.
            json_data = json.loads(response)
            formatted_text = json.dumps(json_data, indent=4, ensure_ascii=False)
        except json.JSONDecodeError:
            # Si no es JSON, guarda el texto tal como está.
            formatted_text = response

        with open('sentencia.txt', 'w', encoding='utf-8') as file:
            file.write(formatted_text)
        print("El texto de la sentencia ha sido guardado en 'sentencia.txt'.")
    else:
        try:
            # Para otras opciones, asume que la respuesta es un JSON y la muestra.
            json_data = json.loads(response)
            for entry in json_data:
                if option in ['1', '3']:
                    # Imprime la información relevante para las opciones 1 y 3.
                    print(f"ID: {entry.get('id', 'No disponible')}, "
                          f"Cendoj ID: {entry.get('cendoj_id', 'No disponible')}, "
                          f"Tribunal: {entry.get('tribunal', 'No disponible')}, "
                          f"Sala: {entry.get('sala', 'No disponible')}, "
                          f"Sede: {entry.get('sede', 'No disponible')}, "
                          f"Sección: {entry.get('seccion', 'No disponible')}, "
                          f"Fecha: {entry.get('fecha', 'No disponible')}, "
                          f"Recurso Número: {entry.get('recurso_n', 'No disponible')}, "
                          f"Juez: {entry.get('juez', 'No disponible')}, "
                          f"Letrado: {entry.get('letrado', 'No disponible')}, "
                          f"Delito: {entry.get('delito', 'No disponible')}")
                elif option == '2':
                    # Imprime la información para la opción 2.
                    print(f"Cendoj ID: {entry.get('cendoj_id', 'No disponible')}, "
                          f"Delito: {entry.get('delito', 'No disponible')}, "
                          f"Juez: {entry.get('juez', 'No disponible')}")
        except json.JSONDecodeError:
            print(response)

def client_interaction(host, port):
    # Interacción principal del cliente.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        while True:
            print("\nMenú:")
            print("1. Consultar todas las sentencias sin el campo texto")
            print("2. Consultar todas las sentencias agrupadas por tipo de delito")
            print("3. Consultar sentencia por ID")
            print("4. Consultar el texto de una sentencia")
            print("0. Salir")
            option = input("Seleccione una opción: ")

            if option == '0':
                break

            send_request(s, option)

            if option in ['3', '4']:
                id_solicitud = input("Ingrese el ID de la sentencia: ")
                send_request(s, id_solicitud)
                response = receive_response(s)
                process_response(response, option)
            else:
                response = receive_response(s)
                process_response(response, option)

if __name__ == "__main__":
    HOST = '10.10.10.20'  # Dirección IP del servidor.
    PORT = 65432          # Puerto del servidor.
    client_interaction(HOST, PORT)
