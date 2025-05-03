import sys
import socket
import threading

# ----------------------------------------
# Sección 1: Filtro de caracteres para hexdump
#   - Calcula de antemano un mapeo de valores byte a caracteres imprimibles
#   - Los bytes no imprimibles se representan como '.'
# ----------------------------------------
HEX_FILTER = ''.join(
    [(len(repr(chr(i))) == 3) and chr(i) or '.' for i in range(256)]
)

# ----------------------------------------
# Sección 2: Función hexdump
# ----------------------------------------
def hexdump(src, length=16, show=True):
    """
    Genera y opcionalmente muestra un volcado hexadecimal de los datos de entrada.

    Args:
        src (bytes o str): Datos a volcar.
        length (int): Número de bytes por línea.
        show (bool): Si es True, imprime el volcado; si es False, devuelve la lista de líneas.

    Returns:
        list[str]: Líneas del volcado si show=False, en caso contrario None.
    """
    # Decodificar bytes a cadena para procesar uniformemente
    if isinstance(src, bytes):
        src = src.decode(errors='replace')

    resultados = []
    # Procesar los datos en bloques de `length`
    for i in range(0, len(src), length):
        trozo = src[i:i + length]                  # Extraer bloque
        imprimible = trozo.translate(HEX_FILTER)   # Mapear a caracteres imprimibles
        hexa = ' '.join(f'{ord(c):02x}' for c in trozo)
        ancho_hex = length * 3                      # Ancho para alineación

        # Formato: desplazamiento, bytes hex, caracteres imprimibles
        resultados.append(f'{i:04x}  {hexa:<{ancho_hex}}  {imprimible}')

    if show:
        # Imprimir cada línea formateada
        for linea in resultados:
            print(linea)
    else:
        # Devolver líneas para procesamiento posterior
        return resultados

# ----------------------------------------
# Sección 3: Función para recibir datos
# ----------------------------------------
def receive_from(connection):
    """
    Lee todos los datos disponibles de un socket hasta que no haya más o expire el tiempo de espera.

    Args:
        connection (socket.socket): Objeto socket conectado.

    Returns:
        bytes: Datos recibidos.
    """
    buffer = b""
    # Tiempo de espera corto para evitar bloqueo indefinido
    connection.settimeout(7)
    try:
        while True:
            datos = connection.recv(4096)
            if not datos:
                break
            buffer += datos
    except Exception:
        # Tiempo de espera expirado o conexión cerrada
        pass
    return buffer

# ----------------------------------------
# Sección 4: Manejadores de paquetes (plantillas)
# ----------------------------------------
def request_handler(buffer):
    """
    Modifica o inspecciona las solicitudes del cliente antes de enviarlas al servidor remoto.

    Args:
        buffer (bytes): Payload original del cliente.

    Returns:
        bytes: Payload modificado o original.
    """
    # TODO: Agregar lógica de manipulación de paquetes
    return buffer


def response_handler(buffer):
    """
    Modifica o inspecciona las respuestas del servidor remoto antes de enviarlas al cliente.

    Args:
        buffer (bytes): Payload original del servidor.

    Returns:
        bytes: Payload modificado o original.
    """
    # TODO: Agregar lógica de manipulación de paquetes
    return buffer

# ----------------------------------------
# Sección 5: Lógica principal del proxy
# ----------------------------------------
def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    """
    Gestiona la comunicación entre el cliente local y el servidor remoto.
    Intercepta, registra y opcionalmente modifica el tráfico en ambas direcciones.

    Args:
        client_socket (socket.socket): Socket conectado al cliente local.
        remote_host (str): Dirección del servidor remoto.
        remote_port (int): Puerto del servidor remoto.
        receive_first (bool): Si es True, recibe datos del servidor antes de enviar solicitud.
    """
    # Conectar con el servidor remoto
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    # Si está configurado, recibir datos iniciales del servidor antes de procesar petición
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)
    else:
        remote_buffer = b""

    # Inspeccionar o modificar buffer de respuesta
    remote_buffer = response_handler(remote_buffer)
    if remote_buffer:
        print(f"[<==] Enviando {len(remote_buffer)} bytes al cliente.")
        client_socket.send(remote_buffer)

    # Bucle principal: reenviar tráfico hasta que alguna conexión cierre
    while True:
        # Leer datos del cliente local
        local_buffer = receive_from(client_socket)
        if local_buffer:
            print(f"[==>] Recibidos {len(local_buffer)} bytes del cliente.")
            hexdump(local_buffer)

            # Inspeccionar o modificar solicitud
            local_buffer = request_handler(local_buffer)
            remote_socket.send(local_buffer)
            print("[==>] Enviado al servidor.")

            # Leer respuesta del servidor remoto
            remote_buffer = receive_from(remote_socket)
            if remote_buffer:
                print(f"[<==] Recibidos {len(remote_buffer)} bytes del servidor.")
                hexdump(remote_buffer)

                # Inspeccionar o modificar respuesta
                remote_buffer = response_handler(remote_buffer)
                client_socket.send(remote_buffer)
                print("[<==] Enviado al cliente.")

        # Condición de salida: no hay datos de un lado u otro
        if not local_buffer or not remote_buffer:
            client_socket.close()
            remote_socket.close()
            print("[*] No hay más datos. Cerrando conexiones.")
            break

# ----------------------------------------
# Sección 6: Bucle de escucha del servidor
# ----------------------------------------
def server_loop(local_host, local_port, remote_host, remote_port, receive_first):
    """
    Configura el socket de escucha y crea un hilo para cada conexión entrante.

    Args:
        local_host (str): Host/IP local donde el proxy escucha.
        local_port (int): Puerto local donde el proxy escucha.
        remote_host (str): Dirección del servidor remoto.
        remote_port (int): Puerto del servidor remoto.
        receive_first (bool): Si es True, recibe datos del servidor antes de procesar solicitudes.
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((local_host, local_port))
    except Exception as e:
        print(f"[!!] Error al enlazar {local_host}:{local_port}: {e}")
        sys.exit(1)

    print(f"[*] Escuchando en {local_host}:{local_port}")
    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print(f"> Conexión entrante de {addr[0]}:{addr[1]}")

        proxy_thread = threading.Thread(
            target=proxy_handler,
            args=(client_socket, remote_host, remote_port, receive_first)
        )
        proxy_thread.start()

# ----------------------------------------
# Sección 7: Punto de entrada
# ----------------------------------------
def main():
    """
    Analiza los argumentos de línea de comandos y arranca el proxy.
    Uso: proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]
    """
    if len(sys.argv) != 6:
        print("Uso: proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
        sys.exit(1)

    local_host = sys.argv[1]
    local_port = int(sys.argv[2])
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])
    receive_first = sys.argv[5].lower() in ('true', 'yes', '1')

    server_loop(local_host, local_port,
                remote_host, remote_port, receive_first)

if __name__ == '__main__':
    main()
