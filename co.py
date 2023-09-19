import socket
import threading
import socketserver
from random import randrange
import sys
from threading import Lock

PUERTO = 12345
mi_eleccion = format(randrange(3))  # Elección aleatoria inicial en Z3
mi_eleccion_lock = Lock()
cons = {} #diccionario de consenso. La llave será la direccion IP. Almacena las decisiones de los vecinos
decisiones = {} #diccionario de decisiones. La llave sera la direccion IP. Almacena las elecciones iniciales de los vecinos.
enviada = [] #Lista de los vecinos a los que ya se envio la informacion
vecinos = ['172.20.6.11', '172.20.6.12']

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        IP_cliente = self.client_address[0]

        #Mensajes de decision
        if data.startswith('D '):
            self.log(data)
            data = self.quitaD(data)
            print("Se recibió: ", data)
            cons[IP_cliente] = data #Guardar las decisiones de los proceso
            response = b':D'
            self.request.sendall(response)
        else: #Mensajes de eleccion inicial
            decisiones[IP_cliente] = data #Guardar la eleccion inicial de los procesos
            self.log(data)
            print("Se recibió: ", data)
            response = b':)'
            self.request.sendall(response)

    def quitaD(self, data):
        return data[2:].strip()

    def log(self, data):
        with open("log.txt", "a") as f:
            mensaje = "Recibido " + data + " de " + self.client_address[0] + "\r\n"
            f.write(mensaje)
            f.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, message):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, PUERTO))
            sock.sendall(bytes(message, 'ascii'))
            sock.close()
            return True
    except:
        return False

def eleccion():
    #Enviar la info a los vecinos
    while len(enviada) != len(vecinos):
        for vecino in vecinos:
            if vecino not in enviada:
                status = client(vecino, mi_eleccion)
                if status:
                    enviada.append(vecino)
    print("Mensajes enviados: ", enviada)
    return

def establece_decision():
    global mi_eleccion
    # Bloquear antes de modificar mi_eleccion
    while len(decisiones) != len(vecinos):
        continue
    with mi_eleccion_lock:
        d = list(decisiones.values())
        d.append(mi_eleccion)
        mayoria = max(d, key=d.count)
        print("La mayoría eligió: ", mayoria)
        mi_eleccion = mayoria
        print("Nueva elección: ", mi_eleccion)

def enviar_decision():
    for vecino in vecinos:
        status = client(vecino, "D " + mi_eleccion)
        if status:
            print("Decision enviada a ", vecino)

def consenso():
    while len(cons) < len(vecinos):
        continue
    if len(set(cons.values())) == 1:
        with open("ganador.txt", "w") as f:
            f.write(mi_eleccion)
            f.close()
        print("Consenso logrado")
    else:
        print("Consenso no logrado")

if __name__ == "__main__":
    HOST = "172.20.6.13"  
    server = ThreadedTCPServer((HOST, PUERTO), ThreadedTCPRequestHandler)
    with server:
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print("Eleccion inicial:", mi_eleccion)
        eleccion()
        establece_decision()
        enviar_decision()
        consenso()
        server.shutdown()
