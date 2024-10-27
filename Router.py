
import time

# Porta solicitada pela professora
PORT = 19000 
# Intervalo de envio das tabelas de roteamento
TIMEOUT_ANNOUNCEMENT = 15  
# Tempo para considerar que o vizinho saiu da rede
TIMEOUT_NEIGHBORS = 35  

# Função para ler os vizinhos a partir de um arquivo
def read_neighbors():
    file = "roteadores.txt"
    neighbors = []
    
    try:
        with open(file, 'r') as lines:
            for line in lines:
                neighbor = line.strip()
                if neighbor:
                    neighbors.append(neighbor)
    except Exception:
        print(f"Erro na leitura do arquivo: {file}")

    return neighbors

# Classe que representa um roteador com seus atributos e sua tabela de roteamento
class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neighbors = read_neighbors()

        self.routing_table = [
                {'ip de destino': neighbor, 'metrica': 1, 'ip de saida': neighbor} 
                for neighbor in self.neighbors
            ]
        
        self.router_last_activity = {
                neighbor: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())) 
                for neighbor in self.neighbors
            }

        # Prints para DEBUG
        print(f"Ip router: {self.ip}") 
        print(f"Neighbors: {self.neighbors}")
        print(f"Routing Table: {self.routing_table}")
        print(f"Routing Last Activity: {self.router_last_activity}")
        self.route_announcement()

    def route_announcement(self):
        if self.routing_table.count != 0:
            sent_message = '!' + '!'.join(
                    f"{entry['ip de saida']}:{entry['metrica']}" for entry in self.routing_table
                )
            
            for neighbor in self.neighbors:
                # Prints para DEBUG
                print(f"Message sended to others neighbors: NEIGHBOR: {neighbor}, MESSAGE: {sent_message}")

# Executa o roteador
if __name__ == "__main__":
    ip_roteador = "127.0.0.1"  
    roteador = Router(ip_roteador)
    