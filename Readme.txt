# Simulador de Tabelas de Roteamento e Envio de Mensagens

## Descrição

Este projeto implementa um **simulador de roteadores** que realiza:  
1. **Troca periódica de tabelas de roteamento entre roteadores vizinhos.**  
2. **Envio e roteamento de mensagens de texto utilizando tabelas de roteamento.**

A comunicação entre roteadores utiliza **sockets UDP** na porta `19000`, respeitando um protocolo de mensagens definido.

---

## Funcionalidades

### Parte 1: Gerenciamento de Tabelas de Roteamento

- **Leitura do arquivo `roteadores.txt`** para configuração dos vizinhos.  
- **Troca de tabelas** de roteamento a cada **15 segundos** entre vizinhos.  
- **Atualização automática** da tabela local:
  - Adicionar novas rotas.
  - Atualizar rotas com melhor métrica.
  - Remover rotas inativas após **35 segundos** de silêncio.  
- Exibição periódica da tabela de roteamento e notificações em caso de alterações.

### Parte 2: Envio de Mensagens de Texto

- **Envio de mensagens de texto** entre roteadores, utilizando a tabela de roteamento.  
- Mensagens são **roteadas** até o destino final.  
- Exibição de logs indicando:
  - Mensagens recebidas.
  - Mensagens roteadas para o próximo roteador.
  - Endereço **de origem**, **de destino** e o **conteúdo** da mensagem.

---

## Protocolo de Comunicação

### Mensagem 1: Anúncio de Rotas  
Formato:  
!IP_DESTINO:MÉTRICA!IP_DESTINO:MÉTRICA

### Mensagem 2: Anúncio de Roteador  
Formato:
@IP_PROPRIO

### Mensagem 3: Mensagem de Texto  
Formato:   
&IP_ORIGEM%IP_DESTINO%MENSAGEM

---

## Pré-requisitos

- **Python 3.x** instalado.  
- Ambiente configurado para execução de sockets UDP.

---

## Configuração e Execução

1. **Configurar vizinhos**  
   Crie um arquivo chamado `roteadores.txt` contendo um endereço IP por linha, representando os vizinhos:  
   192.168.1.2
   192.168.1.3
2. **Executar o programa
   Em cada máquina ou terminal, execute o script principal informando o IP do roteador:
   python roteador.py <IP_PROPRIO>
3. **Enviar mensagens de texto
   Durante a execução, envie uma mensagem utilizando o formato:
   &<IP_ORIGEM>%<IP_DESTINO>%<MENSAGEM>



