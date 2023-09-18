import socket
import threading
import socketserver
from random import randrange
import sys
import re

mi_eleccion = format(randrange(3))
consenso = []
decisiones = []
enviada = []
vecinos = ['172.20.6.11','172.20.6.12']

class ThreadedTCPRequestHandler(socketserver.BaseRequestHandler):

    def handle(self):
        data = str(self.request.recv(1024), 'ascii')
        if 'D' in data:
            self.log(data)
            data = self.quitaD(data)
            print("Se recibio: ", data)
            consenso.append(data)
            response = b':D'
            self.request.sendall(response)
        else:
            decisiones.append(tuple((self.client_address[0],data)))
            self.log(data)
            print("Se recibio: ", data)
            response = b':)'
            self.request.sendall(response)
    
    def quitaD(self, data):
        tmp = re.split("D\ ", data)[1]
        return re.split("\n", tmp)[0]

    def log(self, data):
        with open("log.txt", "a") as f:
            mensaje = "Recibido " + data + " de " + self.client_address[0] + "\r\n"
            f.write(mensaje)
            f.close()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    pass

def client(ip, message, port=12345):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((ip, port))
            sock.sendall(bytes(message, 'ascii'))
            sock.close()
            return 1
    except:
        return 6

def eleccion():
    while len(enviada) != len(vecinos):
        for vecino in vecinos:
            if vecino not in enviada:
                status = client(vecino, mi_eleccion)
                if status != 6:
                    enviada.append(ip)
    print("Mensajes enviados: ", enviada)
    return

def establece_decision():
    d = [x[1] for x in decisiones]
    d.append(mi_eleccion)
    mayoria = max(d, key=d.count)
    print("La mayoria eligio: ", mayoria)
    mi_eleccion = mayoria
    print("Nueva eleccion: ", mi_eleccion)

def enviar_decision():
    for vecino in vecinos:
        status = client(vecino, "D " + mi_eleccion)
        if status != 6:
            print("Decision enviada a ", vecino)

def consenso():
    if len(set(decisiones)) > 1:
        print("consenso no logrado")
    else:
        print(set(decisiones))

#def guardar():
#    with open("resultado.txt","w") as f:
#        f.write(''.join(consenso))
#        f.close()

if __name__ == "__main__":
    HOST, PORT = "172.20.6.13", 12345
    server = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler)
    with server:
        ip, port = server.server_address
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        print(mi_eleccion)
        eleccion()
        establece_decision()
        enviar_decision()
        consenso()
        server.shutdown()
