import time
import socket
import threading

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

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.ip, PORT))

        self.neighbors = read_neighbors()

        self.routing_table = [
                {'ip de destino': neighbor, 'metrica': 1, 'ip de saida': neighbor} 
                for neighbor in self.neighbors
            ]
        
        self.router_last_activity = {
                neighbor: time.time() 
                for neighbor in self.neighbors
            }
        
        # Criando as threads para ficarem operando em paralelo a Main
        threading.Thread(target=self.receive_message, daemon=True).start()
        threading.Thread(target=self.periodic_route_announcement, daemon=True).start()
        threading.Thread(target=self.check_neighbor_activity, daemon=True).start()
        threading.Thread(target=self.display_routing_table, daemon=True).start()

        # Prints para DEBUG
        print(f"Ip router: {self.ip}") 
        print(f"Neighbors: {self.neighbors}")
        print(f"Routing Table: {self.routing_table}")
        print(f"Routing Last Activity: {self.router_last_activity}")

        self.router_advertisement()

    # Método que envia sua tabela de roteamento para os vizinhos (a cada 15 segundos)
    def route_announcement_table(self):
        if self.routing_table.count != 0:
            sent_message = '!' + '!'.join(
                    f"{entry['ip de saida']}:{entry['metrica']}" for entry in self.routing_table if entry['ip de destino'] != self.ip
                )
            
            for neighbor in self.neighbors:
                self.socket.sendto(sent_message.encode(), (neighbor, PORT))
                # Prints para DEBUG
                print(f"Message sended to others neighbors: NEIGHBOR: {neighbor}, MESSAGE: {sent_message}")

    # Método para avisar outros roteadores que ele entrou em uma rede existente
    def router_advertisement(self):
        message_to_advertisement = f"@{self.ip}"
        for neighbor in self.neighbors:
            self.socket.sendto(message_to_advertisement.encode(), (neighbor, PORT))
            # Prints para DEBUG
            print(f"Router Advertisement to NEIGHBOR: {neighbor}: MESSAGE: {message_to_advertisement}")

    # Método para ficar observando quando o usuário receber alguma mensagem
    def receive_message(self):
        while True:
            data, addr = self.socket.recvfrom(1024)
            ip_sended = addr[0]
            message = data.decode()
            self.router_last_activity[ip_sended] = time.time()

            ip_from_message = message[1:]

            if message.startswith('@'):
                self.process_router_announcement(ip_from_message)
            else:
                if message.startswith('!'):
                    self.process_routing_update(message, ip_sended)

    # Método para processar o anúncio de roteadores
    def process_router_announcement(self, announced_ip):
        if announced_ip not in self.neighbors:
            self.neighbors.append(announced_ip)
            
            self.routing_table.append({
                'ip de destino': announced_ip,
                'metrica': 1,
                'ip de saida': announced_ip
            })

            self.router_last_activity[announced_ip] = time.time()

            print(f"O Roteador: {announced_ip} entrou na rede.")

            self.route_announcement_table()


    # Método para processar o anúncio de rotas
    def process_routing_update(self, message, ip_sended):
        updated = False
        received_routes = message.strip('!').split('!')
        received_ips = []

        # Para cada rota recebida:
        for route in received_routes:
            ip_dest, metric = route.split(':')
            metric = int(metric) + 1  # Incrementa a métrica
            received_ips.append(ip_dest)

            # Verifica se a rota existe
            existing_route = next((item for item in self.routing_table if item['ip de destino'] == ip_dest), None)

            # Se a rota não é para ele, continua
            if ip_dest != self.ip:
                # Se ja existe a rota, incrimenta a métrica e atualiza o ip de saida se a métrica é menor 
                if existing_route:
                    if metric < existing_route['metrica']:
                        updated = True

                        existing_route['metrica'] = metric
                        existing_route['ip de saida'] = ip_sended
                        
                        print(f"Atualizada a rota EXISTENTE para o IP: {ip_dest} FEITA PELO IP: {ip_sended} com MÉTRICA: {metric}")
                else:
                    updated = True

                    self.routing_table.append({
                        'ip de destino': ip_dest,
                        'metrica': metric,
                        'ip de saida': ip_sended
                    })
                    
                    print(f"Adicionou uma NOVA rota para o IP: {ip_dest} FEITA PELO IP: {ip_sended} com MÉTRICA: {metric}")
            
        # Remove AS rotas que não foram recebidas por nenhum roteador
        for route in self.routing_table:
            if route['ip de saida'] == ip_sended and route['ip de destino'] not in received_ips and route['ip de destino'] != ip_sended:
                updated = True
                
                self.routing_table.remove(route)
                
                print(f"Removeu a rota para IP DESTINO: {route['ip de destino']} FEITA PELO IP: {ip_sended}")

        # Caso houve atualizações, envia sua tabela para os outros roteadores.
        if updated:
            self.route_announcement_table()
                
    def periodic_route_announcement(self):
        while True:
            self.route_announcement_table()
            time.sleep(TIMEOUT_ANNOUNCEMENT)

    def check_neighbor_activity(self):
        while True:
            current_time = time.time()
            inactive_neighbors = []

            for neighbor, last_activity in self.router_last_activity.items():
                if current_time - last_activity > TIMEOUT_NEIGHBORS:
                    inactive_neighbors.append(neighbor)

            for neighbor in inactive_neighbors:
                print(f"Vizinho NEIGHBOR: {neighbor} está inativo.")
                self.router_last_activity.pop(neighbor)
                self.neighbors.remove(neighbor)

                # Remove rotas associadas ao vizinho
                routes_to_remove = [route for route in self.routing_table if route['ip de saida'] == neighbor]

                for route in routes_to_remove:
                    self.routing_table.remove(route)
                    print(f"Removeu rota para ROTEADOR: {route['ip de destino']} VIA: {neighbor}")

                self.send_routing_table()
            time.sleep(5)

    def display_routing_table(self):
        while True:
            print("\nTabela de Roteamento:")
            for entry in self.routing_table:
                print(f"Destino: {entry['ip de destino']}, Métrica: {entry['metrica']}, Saída: {entry['ip de saida']}")
            time.sleep(10)

# Executa o roteador
if __name__ == "__main__":
    ip_roteador = "127.0.0.1"  
    roteador = Router(ip_roteador)
    